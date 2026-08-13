def clamp(v, lo=0.0, hi=100.0):
    return float(max(lo, min(hi, v)))

def risk_band(score):
    if score >= 75: return "Critical"
    if score >= 55: return "High"
    if score >= 30: return "Moderate"
    return "Low"

def calculate_score(tender_value, bid_count, winning_bid, second_bid,
                    supplier_wins, supplier_share, conflict_signal):
    tender = max(float(tender_value), 1.0)
    winning = max(float(winning_bid), 0.0)
    second = max(float(second_bid), 0.0)
    bids = max(int(bid_count), 1)
    price_dev = abs(winning-tender)/tender*100
    win_gap = 0 if second <= 0 else max(0,(second-winning)/second*100)
    low_comp = max(0,min(100,(5-bids)/4*100))
    concentration = clamp(float(supplier_wins)/20*100)
    price_signal = clamp(price_dev*2)
    gap_signal = clamp(win_gap*2)
    score = (.25*price_signal + .20*gap_signal + .18*low_comp +
             .17*clamp(supplier_share) + .10*concentration +
             .10*clamp(conflict_signal))
    return round(clamp(score),1)
