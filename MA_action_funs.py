from numpy import diff
def get_change(ma):
  # Pn/Po = rate of change of MA
  # Pn = Po x change
  
  x = [i for i in range(len(ma))]
  change = diff(ma)/diff(x)            # change of values
  change = diff(change)                   # rate of change
  change = sum(change)/len(change)        # Avg. rate of change
  change *=30                             # since numbers are very small and doesn't affect the price
  change = round(change,6)
  return change


def Action(price,change):
  Type = ""
  trade = True
  tp,sl = 0,0
  change = float(change)
  if(change>0):             # increasing
    tp = price*(1+change)
    if( (tp-price)*10000 < 20):         # profit is less than 20 pips
      trade = False
    else:
      sl = price - (tp-price)/2      # half profit pips
    type = 'buy'
  else:                    # decreasing
    tp = price*(1+change)
    if((price-tp)*10000 <20):           # profit is less than 20 pips
      trade = False
    else:
      sl = price + (price -tp)/2     # half profit pips
    type = 'sell'


  
