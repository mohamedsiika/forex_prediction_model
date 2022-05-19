def get_change(ma):
  # Pn/Po = rate of change of MA
  # Pn = Po x change
  
  x = [i for i in range(len(ma))]
  change = diff(ma)/diff(x)            # change of values
  change = diff(change)                   # rate of change
  change = sum(change)/len(change)        # Avg. rate of change
  change *=30                             # since numbers are very small and doesn't affect the price
  change +=1                              # to be ready for multiplication with old price
  change = round(change,6)
  return change


def Action(price,change):
  Type = ""
  trade = True
  tp,sl = 0,0
  change = float(change)
  if(change>0):             # increasing
    tp = price*change
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

  print (trade)
  print(type)
  print(tp)
  print(sl)
    

Action(1.0472,get_change(predict_moving))    
  
