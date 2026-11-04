from diagram_engine import *
from diagrams_reg import dia
from diagrams_u2b import solve

XL, YL = 'Real GDP (Y)', 'Price level (PL)'
D0 = ((10, 90), (90, 10)); S0 = ((10, 10), (90, 90))

@dia('business-cycle', 'The business cycle', 't3-1',
     steps=['Label the axes Time and Real GDP.', 'Draw a rising straight trend line: the long-term growth trend (potential output).', 'Draw a wave around it showing actual GDP.', 'Label the phases: expansion (recovery), peak (boom), contraction (recession), trough.'],
     explain='Actual real GDP fluctuates around its long-term trend. Above trend (peak) there is a positive output gap: unemployment falls below its natural rate and inflation tends to rise. Below trend (trough) there is a negative output gap: cyclical unemployment rises and inflation falls. A recession is commonly defined as two consecutive quarters of negative real GDP growth. Growth in the trend comes from rising productive capacity.',
     watch='Recession means real GDP is falling, not just growing slowly. Growth can be positive while the economy is below trend.')
def _():
    g = G('Time', 'Real GDP')
    g.line((0, 22), (100, 72), 'k', 'trend', off=(-40, 18), dash=True)
    import math
    g.fn(lambda x: 22 + 0.5*x + 13*math.sin((x-6)/100*2*math.pi*2.05), 0, 100, 'd', 'actual GDP', off=(-60, -16), step=0.5)
    g.text((18, 45), 'peak', size=11); g.text((43, 26), 'trough', size=11); g.text((30, 52), 'contraction', size=10, italic=True); g.text((55, 50), 'expansion', size=10, italic=True)
    g.text((90, 92), '+ output gap', size=10); g.text((92, 48), '− output gap', size=10)
    return figure(g)

@dia('ad-curve', 'Aggregate demand: movements and shifts', 't3-2',
     steps=['Label axes Price level (PL) and Real GDP (Y).', 'Draw AD sloping down.', 'Show a shift right (AD₁ → AD₂) when C, I, G or (X − M) rise.'],
     explain='AD = C + I + G + (X − M). It slopes down because of the wealth effect (a lower price level raises the real value of wealth), the interest rate effect (a lower price level reduces demand for money and lowers interest rates, raising C and I) and the international trade effect (domestic goods become relatively cheaper, raising X and lowering M). Changes in any component other than the price level shift the curve: consumer confidence, wealth, interest rates, income taxes, household debt, business confidence, technology, government spending, foreign incomes, exchange rates and trade policies.',
     watch='A change in the price level moves along AD; it never shifts it.')
def _():
    g = G(XL, YL); g.line(*D0, 'd', 'AD_1'); g.line((28, 90), (100, 18), 'd', 'AD_2')
    g.arrow((50, 56), (64, 56))
    return figure(g)

@dia('sras', 'Short-run aggregate supply (SRAS)', 't3-2',
     steps=['Draw SRAS sloping upward.', 'Show a leftward shift (SRAS₁ → SRAS₂) after a rise in costs, e.g. oil prices or wages.'],
     explain='In the short run, factor prices (especially money wages) are fixed by contracts, so a higher price level raises profitability and firms supply more. SRAS shifts with changes in costs of production: wages, raw material and energy prices, indirect business taxes and subsidies, and supply shocks (bad weather, war, pandemics, a depreciation raising import costs).',
     watch='A rise in costs shifts SRAS left (up), not right.')
def _():
    g = G(XL, YL); g.line(*S0, 's', 'SRAS_1'); g.line((0, 26), (70, 96), 's', 'SRAS_2', off=(-26, -12))
    g.arrow((54, 52), (40, 52))
    return figure(g)

@dia('nc-lras', 'New classical model: LRAS and long-run equilibrium', 't3-2',
     steps=['Draw a vertical LRAS at the full employment level of output (Yf), also called potential output.', 'Draw AD and SRAS crossing on the LRAS.', 'This is long-run equilibrium: unemployment is at its natural rate.'],
     explain='New classical economists argue that in the long run wages and prices are fully flexible, so the economy returns to potential output whatever the level of AD. LRAS is vertical: output depends only on the quantity and quality of factors of production and technology. Any rise in AD only raises the price level in the long run.',
     watch='Yf is not zero unemployment: there is still natural (frictional and structural) unemployment.')
def _():
    g = G(XL, YL); g.vline(50, 's', 'LRAS', 5, 95, off=(-14, -8))
    D = g.line(*D0, 'd', 'AD'); S = g.line((10, 22), (84, 96), 's', 'SRAS', off=(-14, -12))
    E = meet(D, S); g.drop(E, 'PL_e', 'Y_f'); g.dot(E)
    return figure(g)

@dia('nc-gaps', 'Recessionary (deflationary) and inflationary gaps', 't3-2',
     steps=['Draw LRAS at Yf.', 'Left: AD crosses SRAS to the left of LRAS: real GDP Y₁ < Yf, a recessionary gap.', 'Right: AD crosses SRAS to the right of LRAS: Y₁ > Yf, an inflationary gap.'],
     explain='A recessionary (deflationary) gap means actual output is below potential, with cyclical unemployment. An inflationary gap means output is above potential: resources are over-used, and labour shortages push up wages and prices. Keynesians stress that recessionary gaps can last a long time because wages are sticky downward; new classical economists expect wages to adjust and close the gap on their own.',
     watch='Use "output gap" language and say which side of Yf the economy is on.')
def _():
    out = []
    for title, sh in [('Recessionary gap', -16), ('Inflationary gap', 16)]:
        g = G(XL, YL, title=title, w=300); g.vline(50, 's', 'LRAS', 5, 95, off=(-14, -8))
        D = g.line((10 + sh, 90), (90 + sh, 10), 'd', 'AD', off=(-24, 6)); S = g.line((10, 22), (84, 96), 's', 'SRAS', off=(-22, -12))
        E = meet(D, S); g.drop(E, 'PL_1', 'Y_1'); g.xtick(50, 'Y_f') if abs(E[0]-50) > 6 else None; g.dot(E)
        out.append(g)
    return figure(*out)

@dia('keynes-as', 'Keynesian AS model', 't3-2',
     steps=['Draw an AS curve in three sections: horizontal at low output, then upward-sloping, then vertical at Yf.', 'Draw AD₁ in the horizontal section (deep recession), AD₂ in the middle, AD₃ in the vertical section.'],
     explain='Keynesians argue that in a deep recession there is so much spare capacity that output can rise with no rise in the price level (section 1): firms can hire idle workers without raising wages, and wages are sticky downward so the price level does not fall either. As the economy approaches full employment, bottlenecks appear and costs rise (section 2). At Yf output cannot rise further and extra AD only causes inflation (section 3). Implication: the economy can be stuck in a deflationary gap, so government intervention (expansionary fiscal policy) is needed.',
     watch='The horizontal section shows no inflation while output rises, which is the key Keynesian claim.')
def _():
    g = G(XL, YL)
    g.curve([(0, 26), (30, 26), (42, 28), (55, 36), (64, 50), (68, 66), (69, 95)], 's', 'AS', off=(-8, -8))
    g.line((0, 54), (44, -2), 'd', 'AD_1', off=(-12, -6)); g.line((20, 80), (80, 20), 'd', 'AD_2', off=(-12, -6)); g.line((40, 100), (100, 40), 'd', 'AD_3', off=(-12, -6))
    g.xtick(69, 'Y_f'); g.text((15, 18), 'spare capacity', size=10, italic=True)
    return figure(g)

@dia('lras-shift', 'Long-run growth: LRAS shifting right', 't3-2',
     steps=['New classical: shift the vertical LRAS from Yf₁ to Yf₂.', 'Keynesian: shift the vertical section of AS to the right.', 'Show that potential output has risen.'],
     explain='LRAS shifts right when the quantity or quality of factors of production rises (more labour through immigration or higher participation, more capital through investment, better education and training, better technology, institutional changes such as stronger property rights or less red tape). This is long-term economic growth, the same idea as an outward shift of the PPC. With rising AD and LRAS together, the economy can grow without inflation.',
     watch='Supply-side policies aim at this shift, so link to 3.7.')
def _():
    a = G(XL, YL, title='New classical', w=300); a.vline(40, 's', 'LRAS_1', 5, 95, off=(-22, -8)); a.vline(65, 's', 'LRAS_2', 5, 95, off=(-6, -8))
    a.xtick(40, 'Y_f1'); a.xtick(65, 'Y_f2'); a.arrow((44, 60), (61, 60))
    b = G(XL, YL, title='Keynesian', w=300)
    b.curve([(0, 24), (25, 24), (36, 27), (46, 36), (52, 52), (54, 92)], 's', 'AS_1', off=(-18, -8))
    b.curve([(0, 24), (45, 24), (56, 27), (66, 36), (72, 52), (74, 92)], 's', 'AS_2', off=(0, -8))
    b.arrow((56, 70), (70, 70))
    return figure(a, b)

@dia('inflation-types', 'Demand-pull and cost-push inflation', 't3-3',
     steps=['Left: AD shifts right along SRAS; the price level rises and real GDP rises (demand-pull).', 'Right: SRAS shifts left; the price level rises and real GDP falls (cost-push), giving stagflation.'],
     explain='Demand-pull inflation is caused by rising AD (e.g. consumer borrowing booms, expansionary policy, export booms) when the economy is close to capacity. Cost-push inflation is caused by rising costs (oil price shocks such as 1973 and 2022, wage rises not matched by productivity, depreciation raising import prices). Cost-push is harder to fix: contractionary policy cuts inflation but deepens the fall in output.',
     watch='For cost-push, real GDP falls; for demand-pull, it rises in the short run.')
def _():
    a = G(XL, YL, title='Demand-pull', w=300); S = a.line(*S0, 's', 'SRAS'); D1 = a.line(*D0, 'd', 'AD_1', off=(-18, 8)); D2 = a.line((26, 90), (100, 16), 'd', 'AD_2', off=(-20, -8))
    E1, E2 = meet(D1, S), meet(D2, S); a.drop(E1, 'PL_1', 'Y_1'); a.drop(E2, 'PL_2', 'Y_2'); a.dot(E1); a.dot(E2)
    b = G(XL, YL, title='Cost-push', w=300); D = b.line(*D0, 'd', 'AD'); S1 = b.line(*S0, 's', 'SRAS_1', off=(-40, 0)); S2 = b.line((0, 24), (70, 94), 's', 'SRAS_2', off=(-40, -10))
    E1, E2 = meet(D, S1), meet(D, S2); b.drop(E1, 'PL_1', 'Y_1'); b.drop(E2, 'PL_2', 'Y_2'); b.dot(E1); b.dot(E2)
    return figure(a, b)

@dia('deflation-types', 'Bad and good deflation', 't3-3',
     steps=['Left (bad): AD falls; price level falls and real GDP falls.', 'Right (good): SRAS and LRAS shift right (productivity gains); price level falls while real GDP rises.'],
     explain='Deflation is a sustained fall in the average price level. Demand-side ("bad") deflation comes with falling output and rising unemployment, and can spiral: consumers delay purchases, the real value of debt rises, firms cut wages and jobs (Japan in the 1990s–2010s). Supply-side ("good") deflation results from productivity growth or falling costs and comes with growth.',
     watch='Disinflation (inflation falling but still positive) is not deflation.')
def _():
    a = G(XL, YL, title='Bad (demand-side)', w=300); S = a.line(*S0, 's', 'SRAS'); D1 = a.line(*D0, 'd', 'AD_1'); D2 = a.line((0, 76), (72, 4), 'd', 'AD_2', off=(-34, 8))
    E1, E2 = meet(D1, S), meet(D2, S); a.drop(E1, 'PL_1', 'Y_1'); a.drop(E2, 'PL_2', 'Y_2'); a.dot(E1); a.dot(E2)
    b = G(XL, YL, title='Good (supply-side)', w=300); D = b.line(*D0, 'd', 'AD'); S1 = b.line(*S0, 's', 'AS_1', off=(-28, 0)); S2 = b.line((24, 4), (100, 80), 's', 'AS_2')
    E1, E2 = meet(D, S1), meet(D, S2); b.drop(E1, 'PL_1', 'Y_1'); b.drop(E2, 'PL_2', 'Y_2'); b.dot(E1); b.dot(E2)
    return figure(a, b)

@dia('cyclical-unemp', 'Demand-deficient (cyclical) unemployment', 't3-3',
     steps=['Start in long-run equilibrium at Yf.', 'Shift AD left to AD₂: real GDP falls to Y₂ below Yf.', 'Firms need fewer workers (derived demand), so unemployment rises above the natural rate.'],
     explain='Cyclical unemployment is caused by a fall in AD during a recession. Labour demand is derived from the demand for goods, so falling output means job losses. Keynesians recommend expansionary fiscal and monetary policy to restore AD.',
     watch='This is distinct from structural and frictional unemployment, which remain at Yf (the natural rate).')
def _():
    g = G(XL, YL); g.vline(60, 's', 'LRAS', 5, 95, off=(-14, -8)); S = g.line((10, 12), (88, 90), 's', 'SRAS')
    D1 = g.line((20, 100), (100, 20), 'd', 'AD_1'); D2 = g.line((0, 84), (80, 4), 'd', 'AD_2')
    E1, E2 = meet(D1, S), meet(D2, S); g.drop(E1, 'PL_1', 'Y_f'); g.drop(E2, 'PL_2', 'Y_2'); g.dot(E1); g.dot(E2)
    g.arrow((60, 36), (48, 36))
    return figure(g)

@dia('real-wage-unemp', 'Real-wage (disequilibrium) unemployment', 't3-3',
     steps=['Draw a labour market with real wage on the vertical axis.', 'Draw a real wage W₁ above equilibrium (e.g. trade union power or a minimum wage).', 'The gap between labour supplied and demanded is unemployment.'],
     explain='If real wages are held above the market-clearing level, more people want work than firms will hire. Causes: minimum wage laws, strong unions, wage stickiness. Supply-side economists favour labour market flexibility to reduce this.',
     watch='Use the real wage (W/P), not the money wage.')
def _():
    g = G('Quantity of labour', 'Real wage'); D = g.line(*D0, 'd', 'AD_L'); S = g.line(*S0, 's', 'AS_L')
    E = meet(D, S); y = 68; g.drop(E, 'W_e', 'L_e'); g.hline(y, 'g', 'W_1', 0, 96, off=(-26, -10)); g.dot(E)
    g.drop((D.x_at(y), y), None, 'L_d', 'x'); g.drop((S.x_at(y), y), None, 'L_s', 'x'); g.brace(D.x_at(y), S.x_at(y), y, 'unemployment', below=False)
    return figure(g)

@dia('structural-unemp', 'Structural unemployment in a declining industry', 't3-3',
     steps=['Draw the labour market for one industry (e.g. coal mining).', 'Shift labour demand left (D₁ → D₂) as demand for the product falls or technology replaces workers.', 'Employment falls from L₁ to L₂; the displaced workers lack the skills or location for jobs elsewhere.'],
     explain='Structural unemployment comes from changes in the structure of the economy: changing demand, technological change (automation), globalisation moving production abroad. It is long-term because of occupational immobility (wrong skills) and geographical immobility (wrong place, housing costs, family ties). Policies: retraining, education, relocation subsidies, regional policy, labour market flexibility.',
     watch='Structural unemployment is part of the natural rate, so demand-side policy does not cure it.')
def _():
    g = G('Quantity of labour', 'Wage rate'); S = g.line(*S0, 's', 'S_L'); D1 = g.line(*D0, 'd', 'D_L1'); D2 = g.line((0, 76), (72, 4), 'd', 'D_L2', off=(-30, 10))
    E1, E2 = meet(D1, S), meet(D2, S); g.drop(E1, 'W_1', 'L_1'); g.drop(E2, 'W_2', 'L_2'); g.dot(E1); g.dot(E2)
    return figure(g)

@dia('phillips', 'Short-run and long-run Phillips curves', 't3-3', hl=True,
     steps=['Label axes Inflation rate (%) and Unemployment rate (%).', 'Draw a downward-sloping SRPC (convex).', 'Draw a vertical LRPC at the natural rate of unemployment (NRU).', 'Show a move up SRPC₁ (A → B) then a shift to SRPC₂ as expectations adjust (B → C).'],
     explain='The SRPC shows a short-run trade-off: rising AD lowers unemployment but raises inflation. In the 1970s stagflation (high inflation and unemployment together, after supply shocks) broke the simple relationship. The expectations-augmented view: if government pushes unemployment below the NRU, workers expect higher inflation and demand higher wages, SRAS shifts left, and unemployment returns to the NRU at a higher inflation rate. In the long run there is no trade-off: the LRPC is vertical at the NRU, matching the vertical LRAS.',
     watch='Point C is at the NRU with higher inflation, not lower unemployment.')
def _():
    g = G('Unemployment rate (%)', 'Inflation rate (%)'); g.vline(50, 's', 'LRPC', 3, 96, off=(-14, -8))
    g.curve([(14, 92), (25, 55), (40, 32), (60, 20), (90, 12)], 'd', 'SRPC_1', off=(-14, -12))
    g.curve([(14, 100), (28, 70), (40, 54), (60, 40), (90, 31)], 'd', 'SRPC_2', off=(-14, -12))
    g.dot((50, 25), 'A'); g.dot((34, 40), 'B'); g.dot((50, 47), 'C', off=(6, -8)); g.xtick(50, 'NRU')
    g.arrow((48, 26), (36, 37)); g.arrow((36, 42), (48, 46))
    return figure(g)

@dia('lorenz', 'Lorenz curve and Gini coefficient', 't3-4',
     steps=['Label axes Cumulative % of population (poorest first) and Cumulative % of income.', 'Draw the 45° line of perfect equality.', 'Draw a Lorenz curve bowed below it.', 'Gini = A ÷ (A + B), where A is the area between the line of equality and the curve.'],
     explain='The further the Lorenz curve is from the line of equality, the more unequal the income distribution. The Gini coefficient ranges from 0 (perfect equality) to 1 (one person has all income). Income distribution is typically more equal after taxes and transfers (Nordic countries ≈ 0.25–0.28) than in highly unequal countries (South Africa ≈ 0.63). A shift of the curve towards the line of equality shows a fall in inequality.',
     watch='The poorest are on the left; plot cumulative shares, not each group\'s share.')
def _():
    g = G('Cumulative % of population', 'Cumulative % of income')
    g.line((0, 0), (100, 100), 'k', 'equality', off=(-58, -10))
    L = [(0, 0), (20, 5), (40, 14), (60, 28), (80, 50), (100, 100)]
    C = catmull(L)
    g.area([(0, 0)] + C + [(100, 100)], 'gov', 'A', at=(56, 44))
    g.area(C + [(100, 0)], 'cs', 'B', at=(76, 18))
    g.curve(L, 'd', 'Lorenz', off=(-50, 10))
    return figure(g)

@dia('tax-systems', 'Progressive, proportional and regressive taxes', 't3-4',
     steps=['Label axes Income and Average tax rate (%).', 'Progressive: average rate rises with income.', 'Proportional: flat line.', 'Regressive: average rate falls as income rises.'],
     explain='With a progressive tax the marginal rate is above the average rate, so higher earners pay a larger share of income (most income taxes). A proportional (flat) tax takes the same percentage from everyone. Indirect taxes such as VAT are regressive in effect, because lower-income households spend a larger share of their income.',
     watch='Classify by the average rate, not by the amount paid.')
def _():
    g = G('Income', 'Average tax rate (%)')
    g.curve([(5, 6), (30, 16), (60, 32), (95, 44)], 'g', 'progressive', off=(-80, -12)); g.hline(26, 'k', 'proportional', 5, 95, off=(-74, -10)); g.curve([(5, 48), (30, 30), (60, 18), (95, 11)], 'd', 'regressive', off=(-68, 14))
    return figure(g)

@dia('money-market', 'The money market and interest rates', 't3-5',
     steps=['Label axes Interest rate (i) and Quantity of money.', 'Draw money supply (Sm) vertical, set by the central bank.', 'Draw money demand (Dm) sloping down: higher interest rates raise the opportunity cost of holding money.', 'Show an increase in money supply from Sm₁ to Sm₂ lowering the equilibrium interest rate.'],
     explain='The central bank sets the supply of money (or targets the interest rate by adjusting it). People hold money for transactions, precautionary and speculative reasons; the interest rate is the opportunity cost of holding money rather than bonds. Expansionary monetary policy (raising Sm) lowers the interest rate; contractionary policy raises it.',
     watch='Money supply is vertical because it is fixed by the central bank, not by the interest rate.')
def _():
    g = G('Quantity of money', 'Interest rate (i)'); D = g.line(*D0, 'd', 'D_m'); g.vline(45, 's', 'S_m1', 5, 95, off=(-14, -8)); g.vline(62, 's', 'S_m2', 5, 95, off=(-6, -8))
    for x, l, q in [(45, 'i_1', 'M_1'), (62, 'i_2', 'M_2')]:
        p = (x, D.y_at(x)); g.drop(p, l, q); g.dot(p)
    g.arrow((48, 75), (59, 75))
    return figure(g)

@dia('multiplier', 'The Keynesian multiplier', 't3-6',
     steps=['Draw Keynesian AS with AD₁ in the horizontal or rising section.', 'Show the initial injection (e.g. a rise in G) shifting AD₁ to AD₂.', 'Show the further rise in consumption from rounds of re-spending shifting AD to AD₃.', 'The total rise in real GDP (Y₁ → Y₃) is larger than the initial injection.'],
     explain='An injection raises someone\'s income; part of that income is spent again (the marginal propensity to consume), creating income for others, and so on. Multiplier k = 1/(1 − MPC) = 1/MPW, where MPW = MPS + MPT + MPM. For example, if MPC = 0.8, k = 5 and a $10bn rise in G raises real GDP by up to $50bn. Leakages at each round make the process smaller: higher taxes, saving and imports mean a smaller multiplier.',
     watch='The multiplier works both ways: a fall in injections causes a multiplied fall in GDP.')
def _():
    g = G(XL, YL)
    g.curve([(0, 26), (34, 26), (46, 28), (58, 36), (68, 52), (72, 72), (73, 95)], 's', 'AS', off=(-8, -8))
    for a, l in [(0, 'AD_1'), (14, 'AD_2'), (34, 'AD_3')]:
        g.line((a + 0, 68), (a + 44, 2), 'd', l, off=(-12, -2))
    g.arrow((22, 36), (34, 36)); g.arrow((38, 36), (55, 36))
    g.text((28, 44), 'ΔG', size=11); g.text((48, 44), 'multiplied ΔC', size=11)
    return figure(g)

@dia('crowding-out', 'Crowding out in the loanable funds market', 't3-6',
     steps=['Label axes Real interest rate and Quantity of loanable funds.', 'Draw supply of loanable funds (savings) upward and demand (borrowing) downward.', 'Government borrowing to fund a deficit shifts demand right, raising the interest rate from r₁ to r₂.', 'Private borrowing for investment falls: it is crowded out.'],
     explain='When the government borrows to finance expansionary fiscal policy, it competes with firms for loanable funds. Higher interest rates reduce private investment and interest-sensitive consumption, partly offsetting the rise in AD. Keynesians argue crowding out is small in a recession because savings are high and investment demand is weak.',
     watch='Show the reduced private quantity of funds, not only the higher interest rate.')
def _():
    g = G('Quantity of loanable funds', 'Real interest rate'); S = g.line(*S0, 's', 'S (savings)', off=(-56, -12)); D1 = g.line(*D0, 'd', 'D_1', off=(-6, 10)); D2 = g.line((28, 90), (100, 18), 'd', 'D_2', off=(-14, 14))
    E1, E2 = meet(D1, S), meet(D2, S); g.drop(E1, 'r_1', 'Q_1'); g.drop(E2, 'r_2', 'Q_2'); g.dot(E1); g.dot(E2)
    return figure(g)

# ---------------- Unit 4 ----------------
@dia('comp-adv', 'Absolute and comparative advantage (two-country PPCs)', 't4-1', hl=True,
     steps=['Put one good on each axis.', 'Draw a straight-line PPC for each country (constant opportunity cost).', 'The country with the flatter or steeper curve relative to the other has the lower opportunity cost in one good: that is its comparative advantage.', 'Mark a trading point outside each country\'s own PPC to show gains from trade.'],
     explain='A country has an absolute advantage if it can produce more of a good with the same resources. It has a comparative advantage if it has a lower opportunity cost. Example: Country A can make 60 wheat or 30 cloth (1 cloth costs 2 wheat); Country B can make 40 wheat or 40 cloth (1 cloth costs 1 wheat). B has a comparative advantage in cloth, A in wheat. If each specialises and they trade at a rate between 1 and 2 wheat per cloth, both can consume beyond their PPCs.',
     watch='Comparative advantage is about opportunity cost, not who produces more.')
def _():
    g = G('Cloth', 'Wheat')
    g.line((0, 90), (45, 0), 'd', 'A', off=(4, -6)); g.line((0, 60), (60, 0), 's', 'B', off=(4, -6))
    g.ytick(90, '60'); g.ytick(60, '40'); g.xtick(45, '30'); g.xtick(60, '40')
    g.dot((24, 54), 'A after trade', off=(6, -6)); g.dot((24, 48), None)
    return figure(g)

def _world(g, D, S, pw, lbl='P_w'):
    g.hline(pw, 'k', lbl if lbl else None, 0, 98, off=(-28, -10))
    return S.x_at(pw), D.x_at(pw)

@dia('free-trade', 'Free trade: domestic market with imports', 't4-1',
     steps=['Draw domestic D and S with equilibrium Pd, Qe.', 'Draw the world price Pw below Pd: the world supply is perfectly elastic at Pw for a small country.', 'Domestic firms supply Q₁; consumers buy Q₂; imports = Q₂ − Q₁.'],
     explain='With free trade a small country can import as much as it wants at the world price. Consumers gain (lower price, more choice); domestic producers lose sales and some may exit. The gain in consumer surplus exceeds the loss of producer surplus, so society gains overall. Other benefits: lower costs, economies of scale for exporters, competition and efficiency, access to resources, technology transfer.',
     watch='Imports are read horizontally at Pw, between the supply and demand curves.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D_dom'); S = g.line(*S0, 's', 'S_dom'); E = meet(D, S)
    g.drop(E, 'P_d', 'Q_e'); g.dot(E); q1, q2 = _world(g, D, S, 30, 'S_world = P_w')
    g.drop((q1, 30), None, 'Q_1', 'x'); g.drop((q2, 30), None, 'Q_2', 'x'); g.brace(q1, q2, 30, 'imports')
    return figure(g)

@dia('tariff', 'Tariff: price, quantity and welfare effects', 't4-2', hl=True,
     steps=['Start from free trade at Pw (domestic supply Q₁, demand Q₂).', 'Add the tariff: the world supply line rises to Pw + t.', 'Domestic supply extends to Q₃, demand contracts to Q₄; imports fall to Q₄ − Q₃.', 'Shade government revenue (t × imports), and the two welfare loss triangles (production inefficiency and consumption loss).'],
     explain='A tariff is a tax on imports. Effects: higher domestic price, lower consumption, more domestic production, fewer imports, tariff revenue for the government. Stakeholders: consumers lose consumer surplus; domestic producers gain producer surplus and jobs; the government gains revenue; foreign producers lose sales. The left triangle is a production inefficiency (higher-cost domestic firms replace cheaper imports); the right triangle is lost consumer surplus with no gain to anyone. Example: US tariffs on Chinese goods (2018–) and on steel and aluminium; retaliation followed.',
     watch='Government revenue = tariff per unit × imports after the tariff (Q₄ − Q₃).')
def _():
    g = G(); D = g.line(*D0, 'd', 'D_dom'); S = g.line(*S0, 's', 'S_dom')
    pw, pt = 26, 40
    q1, q2 = S.x_at(pw), D.x_at(pw); q3, q4 = S.x_at(pt), D.x_at(pt)
    g.area([(q3, pw), (q3, pt), (q4, pt), (q4, pw)], 'gov', 'revenue', at=((q3+q4)/2, (pw+pt)/2))
    g.area([(q1, pw), (q3, pt), (q3, pw)], 'dwl'); g.area([(q4, pw), (q4, pt), (q2, pw)], 'dwl')
    g.hline(pw, 'k', 'P_w', 0, 98, off=(-22, 12)); g.hline(pt, 'g', 'P_w + tariff', 0, 98, off=(-70, -10))
    for q, l in [(q1, 'Q_1'), (q3, 'Q_3'), (q4, 'Q_4'), (q2, 'Q_2')]:
        g.drop((q, pw), None, l, 'x')
    return figure(g)

@dia('quota', 'Import quota', 't4-2', hl=True,
     steps=['Start from free trade at Pw.', 'Add the quota amount horizontally to domestic supply above Pw: S + quota.', 'The new price Pq is where S + quota meets D.', 'The area (Pq − Pw) × quota is extra revenue for importers or foreign firms holding licences (quota rent), not the government.'],
     explain='A quota is a physical limit on the quantity of imports. Like a tariff it raises the domestic price, reduces consumption, increases domestic output and reduces imports. Unlike a tariff, the government earns no revenue unless it auctions import licences; the gain goes to whoever holds the licences. The welfare loss is therefore larger than with an equivalent tariff.',
     watch='The S + quota line is parallel to S, shifted right by the quota amount, starting at Pw.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D_dom'); S = g.line(*S0, 's', 'S_dom')
    pw = 26; quota = 20
    Sq = Line((S.x_at(pw) + quota, pw), (90, 90 - quota)); g.line(Sq.p1, (100, 100 - quota), 's', 'S + quota', off=(-60, -6), dash=True)
    Eq = meet(D, Sq); pq = Eq[1]
    q3, q4 = S.x_at(pq), D.x_at(pq)
    g.area([(q3, pw), (q3, pq), (q4, pq), (q4, pw)], 'gov', 'quota rent', at=((q3+q4)/2, (pw+pq)/2))
    g.hline(pw, 'k', 'P_w', 0, 98, off=(-22, 12)); g.drop(Eq, 'P_q', None, 'y'); g.dot(Eq)
    g.drop((q3, pq), None, 'Q_3', 'x'); g.drop((q4, pq), None, 'Q_4', 'x')
    return figure(g)

@dia('prod-subsidy-trade', 'Production subsidy to domestic firms', 't4-2', hl=True,
     steps=['Start from free trade at Pw.', 'Shift domestic supply right to S + subsidy.', 'Domestic output rises from Q₁ to Q₃; consumers still pay Pw and buy Q₂; imports shrink to Q₂ − Q₃.', 'Government cost = subsidy per unit × Q₃.'],
     explain='Subsidies protect domestic producers without raising the consumer price. Domestic firms produce more and imports fall. The cost falls on taxpayers (opportunity cost of government spending). There is a welfare loss from inefficient, higher-cost domestic production. Examples: US and EU agricultural subsidies; subsidies for semiconductor and green-tech industries (US CHIPS Act, Inflation Reduction Act).',
     watch='The price to consumers stays at Pw, so consumption does not change.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D_dom'); S = g.line(*S0, 's', 'S_dom'); Ss = g.line((26, 10), (100, 84), 's', 'S + subsidy', off=(-70, 12))
    pw = 30; q1, q2, q3 = S.x_at(pw), D.x_at(pw), Ss.x_at(pw)
    g.hline(pw, 'k', 'P_w', 0, 98, off=(-22, -10))
    for q, l in [(q1, 'Q_1'), (q3, 'Q_3'), (q2, 'Q_2')]: g.drop((q, pw), None, l, 'x')
    g.area([(0, Ss.y_at(q3)), (0, S.y_at(q3)), (q3, S.y_at(q3)), (q3, pw)], 'gov', 'gov. cost', at=(q3/2, (pw + S.y_at(q3))/2))
    return figure(g)

@dia('export-subsidy', 'Export subsidy', 't4-2', hl=True,
     steps=['Draw a domestic market with Pw above the domestic equilibrium: the country exports Q₂ − Q₁ at Pw.', 'An export subsidy raises the price exporters receive to Pw + s, so they divert sales abroad.', 'Domestic price rises to Pw + s: domestic consumption falls and output rises, so exports grow.'],
     explain='Export subsidies raise the revenue firms earn on each unit exported, so exports rise. Domestic consumers pay more; taxpayers fund the subsidy; foreign producers face unfair competition, and WTO rules generally prohibit such subsidies. It can lead to dumping of surpluses (e.g. historical EU agricultural export refunds).',
     watch='Here Pw is above domestic equilibrium, because the country is an exporter.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D_dom'); S = g.line(*S0, 's', 'S_dom')
    pw, ps = 62, 74
    g.hline(pw, 'k', None, 0, 98); g.ytick(pw, 'P_w'); g.hline(ps, 'g', None, 0, 98); g.ytick(ps, 'P_w+s')
    g.brace(D.x_at(pw), S.x_at(pw), pw, 'exports', below=True); g.brace(D.x_at(ps), S.x_at(ps), ps, 'exports with subsidy', below=False)
    return figure(g)

@dia('forex', 'Floating exchange rate: appreciation and depreciation', 't4-5',
     steps=['Label axes Price of currency X (e.g. US$ per €) and Quantity of currency X.', 'Demand for the currency comes from foreigners buying exports, investing in the country (FDI, portfolio), and speculators.', 'Supply of the currency comes from residents buying imports and investing abroad.', 'Left: demand rises → appreciation. Right: supply rises → depreciation.'],
     explain='In a floating system the exchange rate is set by demand and supply. Demand for a currency rises with higher foreign demand for exports, higher relative interest rates (hot money), inward investment, speculation that it will rise, and central bank buying. Supply rises with higher imports, outward investment, lower relative interest rates and speculation that it will fall. Appreciation makes exports dearer and imports cheaper; depreciation does the opposite.',
     watch='Always say which currency the axes refer to, and express the price in another currency.')
def _():
    a = G('Quantity of €', 'US$ per €', title='Rise in demand → appreciation', w=300); S = a.line(*S0, 's', 'S_€'); D1 = a.line(*D0, 'd', 'D_€1', off=(-24, 8)); D2 = a.line((26, 90), (100, 16), 'd', 'D_€2', off=(-24, -6))
    E1, E2 = meet(D1, S), meet(D2, S); a.drop(E1, 'ER_1', 'Q_1'); a.drop(E2, 'ER_2', 'Q_2'); a.dot(E1); a.dot(E2)
    b = G('Quantity of €', 'US$ per €', title='Rise in supply → depreciation', w=300); D = b.line(*D0, 'd', 'D_€'); S1 = b.line(*S0, 's', 'S_€1', off=(-36, 0)); S2 = b.line((26, 10), (100, 84), 's', 'S_€2')
    E1, E2 = meet(D, S1), meet(D, S2); b.drop(E1, 'ER_1', 'Q_1'); b.drop(E2, 'ER_2', 'Q_2'); b.dot(E1); b.dot(E2)
    return figure(a, b)

@dia('fixed-er', 'Maintaining a fixed exchange rate', 't4-5',
     steps=['Draw D and S for the currency with a fixed rate ER* above the market equilibrium.', 'At ER* there is excess supply of the currency.', 'The central bank buys the excess using foreign currency reserves (shifting D right to D₂), or raises interest rates to attract capital inflows.'],
     explain='Under a fixed (pegged) system the government or central bank commits to a rate against another currency (e.g. the Hong Kong dollar against the US dollar, the Danish krone against the euro). To hold the peg when the currency is under downward pressure, the central bank sells foreign reserves to buy its own currency or raises interest rates; under upward pressure it sells its own currency and builds reserves. Devaluation/revaluation are deliberate changes to the peg.',
     watch='Use devaluation/revaluation for fixed systems and depreciation/appreciation for floating ones.')
def _():
    g = G('Quantity of currency', 'Exchange rate'); S = g.line(*S0, 's', 'S'); D1 = g.line(*D0, 'd', 'D_1'); D2 = g.line((30, 90), (100, 20), 'd', 'D_2', off=(-10, 14))
    E = meet(D1, S); g.drop(E, 'ER_e', None, 'y'); g.dot(E); y = 64
    g.hline(y, 'g', 'ER* (peg)', 0, 98, off=(-50, -10)); g.brace(D1.x_at(y), S.x_at(y), y, 'excess supply', below=True)
    return figure(g)

@dia('j-curve', 'The J-curve', 't4-6', hl=True,
     steps=['Label axes Time and Current account balance (with zero in the middle).', 'Start with a deficit; mark the depreciation.', 'The deficit first gets worse, then improves and moves into surplus: the shape of a J.'],
     explain='After a depreciation, import and export volumes take time to respond (existing contracts, habits, time to find new suppliers), so in the short run demand is price inelastic: the country pays more for the same imports and the current account worsens. Over time, as the Marshall–Lerner condition (PEDx + PEDm > 1) is met, export volumes rise and imports fall, so the balance improves.',
     watch='The vertical axis must allow negative values (deficit below zero).')
def _():
    g = G('Time', 'Current account balance', xaxis_mid=True)
    g.curve([(0, 42), (15, 42), (25, 32), (38, 28), (55, 40), (75, 62), (96, 80)], 'd', 'J-curve', off=(-60, -12))
    g.ytick(70, 'surplus'); g.ytick(30, 'deficit'); g.dot((15, 42), 'depreciation', off=(-30, 22))
    return figure(g)

@dia('poverty-cycle', 'The poverty cycle (trap)', 't4-9',
     steps=['Draw a loop of boxes: low income → low savings → low investment (physical, human and natural capital) → low productivity → low income.', 'Add arrows showing each step causing the next.', 'Show where policies (aid, FDI, microfinance, education spending) could break the cycle.'],
     explain='Low incomes mean households spend almost everything on necessities, so savings are low. Low savings mean little investment in physical capital, education and health. Without capital, productivity stays low, which keeps incomes low. The cycle passes from one generation to the next. Breaking it needs an injection from outside: aid, FDI, remittances, microcredit, government investment in human capital or infrastructure.',
     watch='Name the forms of capital: physical, human, natural and (sometimes) social.')
def _():
    f = Flow(560, 330)
    b = [f.box(200, 18, 160, 50, 'Low income', 'd'), f.box(380, 140, 160, 50, 'Low savings', 'k'), f.box(200, 262, 160, 50, 'Low investment\nin capital', 's'), f.box(20, 140, 160, 50, 'Low productivity', 'k')]
    f.arrow([(360, 50), (450, 50), (450, 140)]); f.arrow([(460, 190), (460, 287), (360, 287)]); f.arrow([(200, 287), (100, 287), (100, 190)]); f.arrow([(100, 140), (100, 43), (200, 43)])
    f.text(280, 152, 'break the cycle:', 'c'); f.text(280, 170, 'aid · FDI · microfinance', 'c'); f.text(280, 188, 'education · health', 'c'); f.text(280, 206, 'infrastructure', 'c')
    return f.render()
