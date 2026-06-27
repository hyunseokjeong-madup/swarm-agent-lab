"""
프로모션 ROI — 할인 판촉의 증분 이익을 마진 잠식까지 반영해 계산.
단위마진(정상)=price·margin, 단위마진(할인)=price·(margin−discount).
증분이익 = 판촉판매량·할인단위마진 − 기준판매량·정상단위마진. 계산 정확.

Usage: python promo_roi.py --baseline-units 1000 --price 50000 --margin 0.4 --discount 0.2 --uplift 0.5
"""
import argparse
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline-units",type=float,required=True); ap.add_argument("--price",type=float,required=True)
    ap.add_argument("--margin",type=float,required=True,help="정상 마진율 0~1")
    ap.add_argument("--discount",type=float,required=True,help="할인율 0~1")
    ap.add_argument("--uplift",type=float,required=True,help="판매량 증가율 0~")
    a=ap.parse_args()
    um_normal=a.price*a.margin
    um_promo=a.price*(a.margin-a.discount)
    base_units=a.baseline_units; promo_units=base_units*(1+a.uplift)
    base_profit=base_units*um_normal
    promo_profit=promo_units*um_promo
    inc=promo_profit-base_profit
    # break-even uplift: promo_units*um_promo = base_units*um_normal
    be_uplift=(um_normal/um_promo-1) if um_promo>0 else float('inf')
    print(f"\n=== PROMO ROI ===")
    print(f"정상: {base_units:,.0f}개 × 단위마진 {um_normal:,.0f} = 이익 {base_profit:,.0f}")
    print(f"판촉: {promo_units:,.0f}개 × 단위마진 {um_promo:,.0f} = 이익 {promo_profit:,.0f}")
    print(f"증분 이익 = {inc:,.0f}  ({'🟢 이득' if inc>0 else '🔴 손해'})")
    if um_promo>0:
        print(f"손익분기 판매증가율 = {be_uplift:+.1%} (이 이상 늘어야 판촉이 이득)")
    else:
        print("⚠️ 할인율 ≥ 마진율 → 팔수록 손해(단위마진 음수)")
if __name__=="__main__": main()
