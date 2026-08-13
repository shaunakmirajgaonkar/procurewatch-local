from scoring import calculate_score, risk_band, clamp

low = calculate_score(1000000,8,980000,990000,2,10,0)
high = calculate_score(1000000,1,300000,900000,20,95,90)
assert 0 <= low <= 100 and 0 <= high <= 100
assert high > low
assert risk_band(10)=="Low"
assert risk_band(40)=="Moderate"
assert risk_band(60)=="High"
assert risk_band(80)=="Critical"
assert clamp(-5)==0 and clamp(150)==100
print("PASS: score bounds")
print("PASS: high-risk scenario > low-risk scenario")
print("PASS: risk bands")
print("PASS: clamping")
print("ALL TESTS PASSED")
