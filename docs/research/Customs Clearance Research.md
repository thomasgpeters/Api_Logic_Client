# Customs clearance research (2026-11-26)

Research for elaborating `samples/Customs` (Bermuda), the author's request: customs clearance and automated
clearance (auto-release). US CBP and the WCO are the references for how modern systems work; Bermuda's own
practice where found. gov.bm could not be fetched from the research session: Bermuda facts come from search
excerpts of gov.bm pages. Items marked *(general)* are standard practice not confirmed against a source here.

## Findings that change the sample

- **Bermuda duty is on the transaction (FOB) value, not CIF**: Public Notice 17, Appendix B - freight,
  insurance and handling are listed separately and deducted from a CIF invoice. (A third-party guide says
  "22.5% on CIF"; the government notice wins.) Keep freight and insurance for statistics (CIF) only.
- **Wharfage: 1.25% of customs value** on most air and sea cargo (cash and accompanied baggage exempt); the
  gov.bm page names St George's and L.F. Wade - not confirmed for Hamilton.
- **Foreign values convert at a weekly exchange rate** (BMD pegged 1:1 to USD); values that feed later
  calculations are rounded first.
- Declarations: the Bermuda Customs Declaration (BCD) through CAPS, lodged at the Hamilton Long Room;
  Customs Procedure Codes 4xxx for imports; reliefs (5th-7th Schedules) need an approved importer.
- Rates: 6.5 % to 33.5 %, typically 22.5-25 %; clothing 6.5 %, medicines and books 0 %; cars 75 % on the first
  BMD 10,000 and 150 % above (a tiered rate).
- Personal allowances: residents BMD 300, visitors BMD 50, plus tobacco and alcohol quantities.
- US de minimis (Section 321, entry type 86) is suspended indefinitely (EO 14324, Sept 2025; Federal Register
  24 June 2026): no $800 rule.

## The US process, in brief

- Manifest in ACE before arrival (master and house bills) *(general)*; ISF "10+2" 24 hours before lading
  (ocean), $5,000 liquidated damages per violation.
- Entry: cargo release (3461 data), then the entry summary (7501) within 10 working days *(general)*; types
  01 consumption, 11 informal, 21 warehouse.
- Periodic Monthly Statement: paid by the 15th working day of the next month.
- Bonds: continuous = 10 % of the last 12 months' duties, taxes and fees, minimum $50,000; single transaction =
  value + duties.
- Liquidation 314 days after entry.
- Fees: MPF 0.3464 % (FY2027: min $34.58, max $670.86); Harbor Maintenance Fee 0.125 %, ocean only.
- Rates: ad valorem, specific (per unit), compound (both); valuation FOB; FTA preference by claim.
- Release is paperless when no hold is open (CBP: manifest, exam, targeting; agencies: FDA, USDA/APHIS,
  EPA, CPSC, FWS); exams non-intrusive (VACIS) or intensive.

## Risk and automatic clearance

- Targeting (ATS) scores manifest, ISF and entry data before arrival; trusted traders (CTPAT tiers, AEO under
  the WCO SAFE Framework, mutual recognition) score lower and are examined less.
- ASYCUDA lanes: **green** automatic release, **yellow** documents, **red** physical exam, **blue** release
  now, audit later; plus random selection; officers can re-route.
- Pre-arrival lodging: released on arrival when green and paid or secured.
- Hold reasons: agency permit, targeting hit, manifest mismatch, value below reference, unpaid duty, bond
  insufficient, prohibited goods, missing documents.

## Candidate additions to the sample

Tables: Currency and ExchangeRate (weekly); BillOfLading (master / house); Broker; Agency and Permit; Hold;
Tariff gains rate type, specific rate and unit, wharfage-exempt, agency, prohibited, reference price;
Importer gains trusted-trader tier and compliance points; Country gains a risk weight.

Rules:
1. A line copies its tariff's ad valorem rate, specific rate, unit, agency and prohibited flags.
2. Value in BMD = foreign value x the week's rate, rounded first.
3. Duty = value x rate + quantity x specific rate (ad valorem, specific, compound).
4. Wharfage = 1.25 % of value unless the tariff is exempt.
5. Relief code on a line: duty 0, only for an approved importer (else refused).
6. Declaration: FOB total, CIF for statistics (+ freight, insurance), duty, wharfage, amount due.
7. Prohibited lines block release; lines needing a permit without an approved one open an agency hold.
8. Open holds counted; release needs none.
9. Risk score (formula): origin country, compliance points, trusted-trader discount, first-time importer,
   value per unit below the reference price, a broken seal.
10. Lane from the score: green, yellow, red; blue for trusted traders flagged for audit; a stored random draw
    sends some to red regardless.
11. Auto-release: green or blue, no open holds, the goods arrived, paid or within the bond - a declaration
    lodged before arrival is released when the ship or aircraft arrives.
12. Payments never exceed the amount due.
13. Master bill's packages = the sum of its house bills' packages, else a manifest hold.
14. A failed inspection lowers the importer's compliance points.
15. Personal declarations: the allowance (300 resident / 50 visitor) comes off before duty.
16. Late security filing (under 24 hours before lading): risk up.
17. Deleting: a released declaration or one with payments cannot be deleted; a tariff in use cannot be.

## Sources

- Bermuda Public Notice 17 Appendix B (valuation, rounding, exchange): https://www.gov.bm/sites/default/files/BCD%20Aggregation%20and%20Calculation%20of%20Values%20Public%20Notice%2017%20Appendix%20B.pdf
- Appendix A (field definitions, CPC): https://www.gov.bm/sites/default/files/BCD%20Field%20Definitions%20and%20Completions%20Instructions%20Public%20Notice%2017%20Appendix%20A.pdf
- Declaring goods (CAPS): https://www.gov.bm/declaring-goods-customs
- Wharfage: https://www.gov.bm/wharfage-fees-imported-goods
- Allowances: https://www.gov.bm/node/13206
- Duty relief guidance: https://www.gov.bm/sites/default/files/2024-04/Guidance_on_Applying_for_Customs_Duty_Relief_for_Businesses_and_Charities.pdf
- Bermuda Customs Tariff: https://www.gov.bm/sites/default/files/2022_v2-Bermuda-Customs-Tariff.pdf
- Shipping information (rate range): https://www.gotobermuda.com/sites/default/files/2022-08/bermuda_customs_generic_shipping_information.pdf
- Zonos (22.5 %, cars): https://zonos.com/docs/guides/country-guides/bermuda
- FY2027 user fees: https://public-inspection.federalregister.gov/2026-15530.pdf
- 19 CFR 24.23: https://www.ecfr.gov/current/title-19/chapter-I/part-24/section-24.23
- De minimis suspension: https://www.federalregister.gov/documents/2026/06/24/2026-12670/indefinite-suspension-of-the-de-minimis-exemption-for-merchandise-arriving-through-all-modes-other
- ISF 19 CFR 149.2: https://www.law.cornell.edu/cfr/text/19/149.2
- Bonds, 19 CFR 113.13: https://www.ecfr.gov/current/title-19/chapter-I/part-113/subpart-B/section-113.13
- Liquidation, 19 CFR 159.9: https://www.ecfr.gov/current/title-19/chapter-I/part-159/subpart-A/section-159.9
- PMS due dates: https://www.cbp.gov/sites/default/files/2024-12/periodic_monthly_statements_due_dates_for_2025_508c_0.pdf
- CTPAT: https://cbp.gov/border-security/ports-entry/cargo-security/c-tpat-customs-trade-partnership-against-terrorism
- Timor-Leste lanes SOP: https://customs.gov.tl/wp-content/uploads/formidable/2/ENG-SOP-Application-of-Risk-Management-to-Clearance-of-Goods-CRP-FINAL_10-Jun-2019.pdf
- Trinidad and Tobago SOP: https://tradeind.gov.tt/wp-content/uploads/2016/02/SOP-Processing-Import-Declarations-FINAL-JUNE-2014.pdf
