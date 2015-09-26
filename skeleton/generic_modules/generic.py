from necessary_import import *

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result   

def close_all_positions(instruments):
    for inst in instruments:
        order_target_percent(inst, 0)
    
    return
    
#def close_all_hedge(context):
#    if context:
#        order_target_percent(context.instrument['hedge_treasury'], 0)    
#    return
    
def is_nan_price (price):
    NbNan = np.count_nonzero(np.isnan(price))
    if NbNan > 0:
        return True
    else:
        False
        
def get_weight_list(nb_list, start, finish, increment, precision=2):
    weights = np.arange(start, finish+increment,increment)
    lists = []
    lw = []
    lw = [round(x,2) for x in list(np.around(weights, precision))]
    
    for x in range(nb_list):
        lists.append(lw)
    return lists

def get_permutation(wl, op=operator.eq, condition_value=1, topn = 0):
    '''
    s: a list of weight
    op: operator conditioning the permutation validity (ex: summ weight is 100%)
    
    return: list of potential allocation weights
    '''
    ll=list(itertools.product(*wl))
    ll = ll[1:]
    
    if topn > 0:
        # get max number instrument (forcing a maximum nb of non-zero)
        sm_topn = [op(len(np.nonzero(np.asarray(it))[0]), topn) for it in ll]
        ind = [index for index,value in enumerate(sm_topn) if value==True]
        ll = [ll[i] for i in ind]
        # get min weight for each instrument
        sm_min = [max(it)<=0.6 for it in ll]
        ind = [index for index,value in enumerate(sm_min) if value==True]
        ll = [ll[i] for i in ind]
        
    sm=[op(sum(item), condition_value) for item in ll]
    indices=[index for index,value in enumerate(sm) if value==True]
    
    return [ll[i] for i in indices]
    
def combine_dicts(a, b=None, op=operator.add, force_absolute_values = False):
    if b == None:
        return a
    if force_absolute_values:
        return dict(a.items() + b.items() + [(k, op(abs(a[k]), abs(b[k]))) for k in set(b) & set(a)])
    else:
        return dict(a.items() + b.items() + [(k, op(a[k], b[k])) for k in set(b) & set(a)])
    
def create_zero_target_percent(inst): 
    default_values = np.zeros(len(inst))
    return dict(zip(inst,default_values))
