"""예산 페이싱 알림 (budget pacing). 소진 추세 → 예상 소진·일일 목표·과/저소진 경보."""
import argparse
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spend", type=float, required=True)
    ap.add_argument("--budget", type=float, required=True)
    ap.add_argument("--elapsed", type=int, required=True, help="경과 일수")
    ap.add_argument("--total", type=int, required=True, help="총 일수")
    a = ap.parse_args()
    rate = a.spend / a.elapsed if a.elapsed else 0
    projected = rate * a.total
    pct = projected / a.budget if a.budget else 0
    remain_days = max(0, a.total - a.elapsed)
    daily_target = (a.budget - a.spend) / remain_days if remain_days else 0
    status = "🟢 ON-PACE"
    if pct > 1.05: status = "🔴 OVER-PACE (예산 초과 예상)"
    elif pct < 0.95: status = "🟡 UNDER-PACE (예산 미달 예상)"
    print(f"\n=== PACING ===")
    print(f"소진 {a.spend:,.0f} / 예산 {a.budget:,.0f}  ({a.spend/a.budget:.1%})  · 경과 {a.elapsed}/{a.total}일")
    print(f"일평균 {rate:,.0f} → 예상 총소진 {projected:,.0f} ({pct:.1%} of budget)")
    print(f"남은 {remain_days}일 동안 일일 목표 {daily_target:,.0f}  →  {status}")
if __name__ == "__main__": main()
