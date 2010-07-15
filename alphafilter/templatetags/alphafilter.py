from django.utils.translation import ugettext as _
from django.template import Library

register = Library()

def _get_available_letters(field_name, db_table):
    from django.db import connection, transaction
    from django.conf import settings
    qn = connection.ops.quote_name
    sql = "SELECT DISTINCT UPPER(SUBSTR(%s, 1, 1)) as letter FROM %s" \
                % (qn(field_name), qn(db_table))
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall() or ()
    return set([row[0] for row in rows])


def alphabet(cl):
    if not getattr(cl.model_admin, 'alphabet_filter', False):
        return
    field_name = cl.model_admin.alphabet_filter
    alpha_field = '%s__istartswith' % field_name
    alpha_lookup = cl.params.get(alpha_field, '')
    link = lambda d: cl.get_query_string(d)
    
    import string
    letters_used = _get_available_letters(field_name, cl.model._meta.db_table)
    all_letters = list(set([x for x in string.uppercase+string.digits]) | letters_used)
    all_letters.sort()
    
    choices = [{
        'link': link({alpha_field: letter}), 
        'title': letter,
        'active': letter == alpha_lookup,
        'has_entries': letter in letters_used,} for letter in all_letters]
    all_letters = [{
        'link': cl.get_query_string(None,alpha_field),
        'title': _('All'),
        'active': '' == alpha_lookup,
        'has_entries': True
    },]
    return {'choices': all_letters + choices}
alphabet = register.inclusion_tag('admin/alphabet.html')(alphabet)

