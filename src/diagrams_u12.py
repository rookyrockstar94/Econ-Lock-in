from diagram_engine import *
from diagrams_reg import dia

D0 = ((10, 90), (90, 10)); S0 = ((10, 10), (90, 90))

# ---------------- Unit 1 ----------------
@dia('ppc', 'Production possibilities curve (PPC)', 't1-1',
     steps=['Label the axes with two goods (e.g. Capital goods, Consumer goods), not price and quantity.',
            'Draw a curve bowed out from the origin (concave) meeting both axes.',
            'Mark a point on the curve (efficient), inside it (unemployed or inefficiently used resources) and outside it (unattainable with current resources and technology).',
            'Show a move along the curve with drop lines to read off the opportunity cost.'],
     explain='Every point on the PPC uses all resources efficiently. Moving from A to B gains more of good X but costs some of good Y: that sacrifice is the opportunity cost. The bowed-out shape reflects increasing opportunity cost, because resources are not equally suited to producing both goods.',
     watch='The curve is concave to the origin, not a straight line, unless the question says opportunity cost is constant. Point C inside the curve shows unemployment or inefficiency, not "low demand".')
def _():
    g = G('Good X (e.g. consumer goods)', 'Good Y (e.g. capital goods)')
    c = g.curve([(0, 88), (30, 82), (55, 66), (74, 44), (88, 0)], 'k', 'PPC', off=(-6, -14))
    A = (30, 82); B = (55, 66)
    g.dot(A, 'A'); g.dot(B, 'B'); g.dot((32, 40), 'C', off=(8, 4)); g.dot((80, 72), 'D')
    g.drop(A, 'Y_1', 'X_1'); g.drop(B, 'Y_2', 'X_2')
    g.text((32, 33), 'inefficient / unemployment', size=11, italic=True)
    g.text((82, 80), 'unattainable', size=11, italic=True)
    return figure(g)

@dia('ppc-growth', 'Economic growth on a PPC', 't1-1',
     steps=['Draw the original PPC (PPC₁).', 'Draw a second PPC further from the origin (PPC₂) for potential growth.', 'Show an arrow from a point inside PPC₁ to a point on it for actual growth (using idle resources).', 'Label both kinds of growth.'],
     explain='An outward shift of the whole curve shows an increase in productive capacity (potential growth), caused by more or better factors of production or better technology. A move from inside the curve towards it is actual growth: output rises because unemployed resources are put back to work. An inward shift follows destruction of resources (war, natural disaster, emigration).',
     watch='A shift outward only for one good (biased shift) shows a technological change in that industry only; pivot the curve on the other axis.')
def _():
    g = G('Consumer goods', 'Capital goods')
    g.curve([(0, 70), (25, 65), (45, 52), (60, 32), (68, 0)], 'k', 'PPC_1', off=(-8, -14))
    g.curve([(0, 92), (32, 86), (58, 69), (78, 42), (90, 0)], 'k', 'PPC_2', off=(-8, -14))
    g.dot((25, 35), 'A'); g.dot((42, 55), 'B', off=(-14, -6))
    g.arrow((26, 37), (40, 53)); g.arrow((52, 62), (62, 75)); g.arrow((60, 26), (74, 36))
    g.text((20, 26), 'actual growth', size=11, italic=True)
    g.text((86, 62), 'potential growth', size=11, italic=True)
    return figure(g)

@dia('ppc-cap-cons', 'Capital vs consumer goods: present choices and future growth', 't1-1',
     steps=['Draw two identical PPCs side by side with capital goods on the vertical axis.', 'On the left, mark a point with a high share of capital goods; on the right, a point with a low share.', 'Draw a larger future PPC for the left country and a smaller shift for the right.'],
     explain='An economy that sacrifices consumption today to produce more capital goods (point A) grows faster: next period its PPC shifts out further. This is the opportunity cost of growth, and a key link to development economics (savings gap, Harrod-Domar intuition).',
     watch='Both economies start on the same PPC so that the only difference is the choice made.')
def _():
    a = G('Consumer goods', 'Capital goods', title='Economy 1: invests more', w=300)
    a.curve([(0, 62), (22, 58), (40, 45), (55, 26), (62, 0)], 'k', 'today', off=(-20, -10))
    a.curve([(0, 92), (32, 86), (58, 68), (78, 40), (90, 0)], 'k', 'future', off=(-24, -10))
    a.dot((22, 58), 'A')
    b = G('Consumer goods', 'Capital goods', title='Economy 2: consumes more', w=300)
    b.curve([(0, 62), (22, 58), (40, 45), (55, 26), (62, 0)], 'k', 'today', off=(-20, -10))
    b.curve([(0, 70), (25, 66), (46, 52), (62, 30), (70, 0)], 'k', 'future', off=(-4, -10))
    b.dot((52, 31), 'B')
    return figure(a, b)

@dia('circular-flow', 'Circular flow of income (open economy with government)', 't3-1',
     steps=['Draw households and firms with the real flow (factors and goods) and the money flow (incomes and spending) between them.', 'Add the three leakages out of the flow: savings (S), taxes (T) and import spending (M).', 'Add the three injections back in: investment (I), government spending (G) and export revenue (X).', 'Label the financial sector, the government and the rest of the world.'],
     explain='Households supply factors of production and receive factor incomes (wages, rent, interest, profit); they spend that income on firms\' output. National output = national income = national expenditure. If injections (I + G + X) are greater than leakages (S + T + M), the flow grows; if leakages are greater, it shrinks. Equilibrium national income occurs where I + G + X = S + T + M.',
     watch='Investment means firms buying capital goods, not people buying shares. Imports are a leakage because the spending goes to foreign firms.')
def _():
    f = Flow(660, 380)
    f.box(30, 150, 150, 70, 'Households', 'd')
    f.box(480, 150, 150, 70, 'Firms', 's')
    f.arrow([(180, 170), (480, 170)], 'Spending on goods and services (C)', at=(330, 162), cls='d')
    f.arrow([(480, 205), (180, 205)], 'Factor incomes: wages, rent, interest, profit', at=(330, 226), cls='s')
    f.box(255, 20, 150, 48, 'Financial sector', 'k')
    f.box(255, 300, 150, 48, 'Government', 'k')
    f.box(500, 300, 140, 48, 'Rest of world', 'k')
    f.arrow([(105, 150), (105, 44), (255, 44)], 'Savings (S)', at=(150, 36), cls='g')
    f.arrow([(405, 44), (555, 44), (555, 150)], 'Investment (I)', at=(500, 36), cls='c')
    f.arrow([(80, 220), (80, 324), (255, 324)], 'Taxes (T)', at=(150, 316), cls='g')
    f.arrow([(405, 316), (470, 316), (470, 220)], 'Gov. spending (G)', at=(430, 290), cls='c')
    f.arrow([(130, 220), (130, 366), (570, 366), (570, 348)], 'Import spending (M)', at=(300, 362), cls='g')
    f.arrow([(610, 300), (610, 220)], 'Exports (X)', at=(604, 262), cls='c', anchor='end')
    f.text(330, 120, 'leakages (S, T, M)  ·  injections (I, G, X)', 'k')
    return f.render()

# ---------------- 2.1 Demand ----------------
@dia('demand-move', 'Movement along the demand curve', 't2-1',
     steps=['Label the axes Price (P) and Quantity (Q).', 'Draw a downward-sloping demand curve D.', 'Mark the starting point A at P₁, Q₁ with drop lines.', 'Mark B at a higher price (contraction) and C at a lower price (extension).'],
     explain='A change in the good\'s own price causes a movement along the curve, never a shift. A rise from P₁ to P₂ causes a contraction in quantity demanded (A→B); a fall to P₃ causes an extension (A→C). The law of demand: ceteris paribus, price and quantity demanded are inversely related.',
     watch='Say "quantity demanded" changes, not "demand", when price changes.')
def _():
    g = G()
    D = g.line(*D0, 'd', 'D')
    A = (50, D.y_at(50)); B = (32, D.y_at(32)); C = (68, D.y_at(68))
    for p, l, a, b in [(A, 'A', 'P_1', 'Q_1'), (B, 'B', 'P_2', 'Q_2'), (C, 'C', 'P_3', 'Q_3')]:
        g.drop(p, a, b); g.dot(p, l)
    g.arrow((48, 56), (35, 69)); g.arrow((53, 45), (65, 33))
    return figure(g)

@dia('demand-shift', 'Shifts of the demand curve', 't2-1',
     steps=['Draw the original demand curve D₁.', 'Draw D₂ to the right (increase in demand) and D₃ to the left (decrease).', 'Use one price line P₁ to show that more (Q₂) or less (Q₃) is demanded at every price.'],
     explain='A change in any non-price determinant shifts the whole curve: income (normal or inferior good), tastes and preferences, prices of related goods (substitutes and complements), the number of consumers, future price expectations, advertising, demographic change. A rightward shift means more is demanded at every price.',
     watch='Arrows go horizontally between curves; do not draw a new curve that crosses the old one.')
def _():
    g = G()
    g.line(*D0, 'd', 'D_1')
    D2 = g.line((26, 90), (100, 16), 'd', 'D_2')
    D3 = g.line((0, 84), (72, 12), 'd', 'D_3')
    y = 50; g.hline(y, 'k', None, 0, D2.x_at(y), dash=True); g.ytick(y, 'P_1')
    for x, l in [(50, 'Q_1'), (D2.x_at(y), 'Q_2'), (D3.x_at(y), 'Q_3')]:
        g.drop((x, y), None, l, 'x')
    g.arrow((54, 62), (66, 62)); g.arrow((46, 38), (35, 38))
    return figure(g)

# ---------------- 2.2 Supply ----------------
@dia('supply-move', 'Movement along the supply curve', 't2-2',
     steps=['Draw an upward-sloping supply curve S.', 'Mark A at P₁, Q₁.', 'A higher price P₂ gives an extension in quantity supplied (B); a lower price a contraction (C).'],
     explain='The law of supply: ceteris paribus, a higher price raises quantity supplied because production becomes more profitable and firms can cover the rising marginal cost of extra output (HL: the supply curve reflects increasing marginal costs, caused by diminishing marginal returns).',
     watch='A price change never shifts the supply curve of that good.')
def _():
    g = G(); S = g.line(*S0, 's', 'S')
    A = (50, 50); B = (68, 68); C = (32, 32)
    for p, l, a, b in [(A, 'A', 'P_1', 'Q_1'), (B, 'B', 'P_2', 'Q_2'), (C, 'C', 'P_3', 'Q_3')]:
        g.drop(p, a, b); g.dot(p, l, off=(8, 10))
    g.arrow((54, 57), (64, 67)); g.arrow((46, 43), (36, 33))
    return figure(g)

@dia('supply-shift', 'Shifts of the supply curve', 't2-2',
     steps=['Draw S₁.', 'Draw S₂ to the right (increase in supply) and S₃ to the left (decrease).', 'Show the change in quantity supplied at the same price P₁.'],
     explain='Non-price determinants of supply: costs of factors of production (wages, raw materials, energy), technology, prices of related goods (joint supply and competitive supply), expectations, indirect taxes and subsidies, the number of firms, and shocks such as weather or disasters. A fall in costs shifts S to the right.',
     watch='An increase in supply is a shift to the right (downwards), not upwards.')
def _():
    g = G(); g.line(*S0, 's', 'S_1')
    S2 = g.line((26, 6), (100, 80), 's', 'S_2'); S3 = g.line((0, 18), (76, 94), 's', 'S_3')
    y = 50; g.hline(y, 'k', None, 0, S2.x_at(y), dash=True); g.ytick(y, 'P_1')
    for x, l in [(50, 'Q_1'), (S2.x_at(y), 'Q_2'), (S3.x_at(y), 'Q_3')]:
        g.drop((x, y), None, l, 'x')
    g.arrow((56, 40), (67, 40)); g.arrow((44, 62), (33, 62))
    return figure(g)

# ---------------- 2.3 Equilibrium ----------------
@dia('equilibrium', 'Market equilibrium, excess supply and excess demand', 't2-3',
     steps=['Draw D and S crossing at E; mark Pe and Qe.', 'Draw a price P₁ above Pe: the gap between Qs and Qd is excess supply (surplus).', 'Draw a price P₂ below Pe: the gap is excess demand (shortage).', 'Show arrows pushing price back towards Pe.'],
     explain='At P₁ firms supply more than consumers want, stocks build up and firms cut prices; quantity demanded extends and quantity supplied contracts until the surplus is gone. At P₂ consumers compete for scarce goods, price is bid up, and the shortage disappears. Only at Pe do plans of buyers and sellers match: the market clears.',
     watch='Label the gaps with the quantities on the axis, e.g. excess supply = Qs − Qd.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D'); S = g.line(*S0, 's', 'S')
    E = meet(D, S); g.drop(E, 'P_e', 'Q_e'); g.dot(E, 'E', off=(8, 4))
    y1, y2 = 70, 30
    g.hline(y1, 'k', None, 0, S.x_at(y1), dash=True); g.ytick(y1, 'P_1')
    g.hline(y2, 'k', None, 0, D.x_at(y2), dash=True); g.ytick(y2, 'P_2')
    g.brace(D.x_at(y1), S.x_at(y1), y1, 'excess supply', below=False)
    g.brace(S.x_at(y2), D.x_at(y2), y2, 'excess demand', below=True)
    return figure(g)

@dia('eq-demand-up', 'Increase in demand: new equilibrium', 't2-3',
     steps=['Draw D₁ and S with equilibrium E₁ (P₁, Q₁).', 'Shift demand right to D₂.', 'At P₁ there is now excess demand; price rises to P₂ and quantity to Q₂ at E₂.'],
     explain='An increase in demand (e.g. rising income for a normal good) creates a shortage at the old price. The price rises, signalling to producers to expand output (extension along S) and rationing the good to those willing to pay more. New equilibrium: higher price and higher quantity.',
     watch='Supply does not shift; there is a movement along it.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D_1'); S = g.line(*S0, 's', 'S')
    D2 = g.line((30, 90), (100, 20), 'd', 'D_2')
    E1 = meet(D, S); E2 = meet(D2, S)
    g.drop(E1, 'P_1', 'Q_1'); g.drop(E2, 'P_2', 'Q_2'); g.dot(E1, 'E_1', off=(8, 6)); g.dot(E2, 'E_2', off=(-24, -6))
    g.arrow((40, 68), (54, 68))
    return figure(g)

@dia('eq-supply-up', 'Increase in supply: new equilibrium', 't2-3',
     steps=['Draw D and S₁ with equilibrium E₁.', 'Shift supply right to S₂ (e.g. lower costs).', 'Price falls to P₂ and quantity rises to Q₂.'],
     explain='Lower costs or better technology raise supply. At the old price there is a surplus, so price falls, quantity demanded extends and the market settles at a lower price and higher quantity.',
     watch='Demand does not shift.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D'); S = g.line(*S0, 's', 'S_1')
    S2 = g.line((30, 10), (100, 80), 's', 'S_2')
    E1 = meet(D, S); E2 = meet(D, S2)
    g.drop(E1, 'P_1', 'Q_1'); g.drop(E2, 'P_2', 'Q_2'); g.dot(E1, 'E_1', off=(-26, -4)); g.dot(E2, 'E_2', off=(8, 6))
    g.arrow((40, 28), (54, 28))
    return figure(g)

@dia('surplus', 'Consumer and producer surplus', 't2-3',
     steps=['Draw D and S with equilibrium at Pe, Qe.', 'Shade the area below D and above Pe: consumer surplus.', 'Shade the area above S and below Pe: producer surplus.', 'Together they are social (community) surplus, which is maximised at equilibrium.'],
     explain='Consumer surplus is the difference between what consumers are willing to pay (shown by the demand curve) and what they actually pay. Producer surplus is the difference between the price producers receive and the lowest price they would accept (shown by the supply curve). In a competitive market with no externalities, social surplus is maximised at Pe, Qe: allocative efficiency, where marginal benefit = marginal cost.',
     watch='Both triangles end at Qe; nothing to the right of Qe is surplus.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D = MB'); S = g.line(*S0, 's', 'S = MC')
    E = meet(D, S)
    g.area([(0, D.y_at(0)), E, (0, E[1])], 'cs', 'CS', at=(20, 66))
    g.area([(0, S.y_at(0)), E, (0, E[1])], 'ps', 'PS', at=(20, 34))
    g.drop(E, 'P_e', 'Q_e'); g.dot(E)
    return figure(g)

# ---------------- 2.5 Elasticities ----------------
@dia('ped-compare', 'Price elastic vs price inelastic demand', 't2-5',
     steps=['Draw two panels with the same price change from P₁ to P₂.', 'Left: a flatter demand curve, so quantity changes a lot (elastic, PED > 1).', 'Right: a steep curve, so quantity barely changes (inelastic, PED < 1).'],
     explain='With elastic demand the proportionate change in quantity is greater than the proportionate change in price; with inelastic demand it is smaller. Determinants: number and closeness of substitutes, necessity vs luxury, proportion of income spent, time to adjust, addictiveness, and how broadly the product is defined.',
     watch='Slope and elasticity are not the same thing; compare them only from the same starting point and scale.')
def _():
    a = G(title='Elastic demand (PED > 1)', w=300); D = a.line((0, 70), (100, 30), 'd', 'D', off=(-8, -12))
    p1, p2 = (30, D.y_at(30)), (70, D.y_at(70)); a.drop(p1, 'P_1', 'Q_1'); a.drop(p2, 'P_2', 'Q_2'); a.dot(p1); a.dot(p2)
    b = G(title='Inelastic demand (PED < 1)', w=300); D = b.line((40, 95), (60, 5), 'd', 'D')
    q1, q2 = (D.x_at(61), 61), (D.x_at(39), 39); b.drop(q1, 'P_1', 'Q_1'); b.drop(q2, 'P_2', 'Q_2'); b.dot(q1); b.dot(q2)
    return figure(a, b)

@dia('ped-linear', 'PED varies along a straight-line demand curve', 't2-5', hl=True,
     steps=['Draw a straight-line demand curve meeting both axes.', 'Mark its midpoint: PED = 1 (unit elastic) and total revenue is maximised.', 'Label the upper half "elastic (PED > 1)" and the lower half "inelastic (PED < 1)".', 'Optionally draw a total revenue curve below, peaking at the midpoint quantity.'],
     explain='On a linear demand curve the slope is constant, but PED = (ΔQ/ΔP) × (P/Q) changes because P/Q changes. At high prices and low quantities the percentage change in Q is large relative to the percentage change in P, so demand is elastic; at low prices it is inelastic. Firms facing elastic demand raise revenue by cutting price; firms facing inelastic demand raise revenue by raising price.',
     watch='This is why a single "flat = elastic" rule is unreliable; a constant slope does not mean constant PED.')
def _():
    a = G(title='Demand', w=310); D = a.line((0, 90), (90, 0), 'd', 'D', off=(-10, -10))
    m = (45, 45); a.drop(m, 'P_m', 'Q_m'); a.dot(m, 'PED = 1', off=(8, -6))
    a.text((26, 74), 'PED > 1 (elastic)', anchor='start', size=11); a.text((60, 18), 'PED < 1', anchor='start', size=11)
    a.text((70, 84), 'PED = ∞ at top', size=10, italic=True); a.text((78, 8), 'PED = 0', size=10, italic=True)
    b = G('Quantity', 'Total revenue', title='Total revenue', w=310)
    b.curve([(0, 0), (20, 60), (45, 90), (70, 60), (90, 0)], 'g', 'TR', off=(-24, -10))
    b.drop((45, 90), 'TR max', 'Q_m', to='x'); b.ytick(90, 'max')
    return figure(a, b)

@dia('ped-special', 'Special cases of PED', 't2-5',
     steps=['Perfectly inelastic: a vertical line (PED = 0).', 'Perfectly elastic: a horizontal line (PED = ∞).', 'Unit elastic: a rectangular hyperbola (PED = 1), where every price × quantity rectangle has the same area.'],
     explain='Perfectly inelastic demand means quantity does not respond at all to price (an approximation for life-saving drugs). Perfectly elastic demand means any rise in price loses all sales (an individual firm in perfect competition). Along a unit elastic curve, total revenue is the same at every price.',
     watch='The unit elastic case is a curve, not a 45° line.')
def _():
    a = G(title='PED = 0', w=200); a.R = 14; a.line((50, 5), (50, 95), 'd', 'D')
    b = G(title='PED = ∞', w=200); b.R = 14; b.line((5, 50), (95, 50), 'd', 'D', off=(-14, -12))
    c = G(title='PED = 1', w=220); c.R = 14
    c.curve([(12, 95), (20, 57), (30, 38), (45, 25.3), (65, 17.5), (95, 12)], 'd', 'D', off=(-10, -12))
    c.area([(0, 0), (0, 38), (30, 38), (30, 0)], 'gov'); c.area([(0, 0), (0, 17.5), (65, 17.5), (65, 0)], 'cs')
    return figure(a, b, c, gap=10)

@dia('ped-tr', 'Price change, PED and total revenue', 't2-5',
     steps=['Draw a steep (inelastic) demand curve.', 'Show a price rise from P₁ to P₂ and the fall in quantity from Q₁ to Q₂.', 'Shade the revenue gained (P₂−P₁)×Q₂ and the revenue lost (Q₁−Q₂)×P₁.'],
     explain='When demand is price inelastic, a rise in price increases total revenue because the revenue gained from the higher price on units still sold is larger than the revenue lost on units no longer sold. When demand is elastic the opposite holds, so firms gain by cutting prices. This is why governments tax goods with inelastic demand (tobacco, fuel) to raise revenue.',
     watch='TR = P × Q, the rectangle under the point on the demand curve.')
def _():
    g = G(); D = g.line((35, 95), (65, 5), 'd', 'D')
    p1 = (D.x_at(40), 40); p2 = (D.x_at(65), 65)
    g.area([(0, 40), (0, 65), (p2[0], 65), (p2[0], 40)], 'prof', 'gain', at=(22, 52.5))
    g.area([(p2[0], 0), (p2[0], 40), (p1[0], 40), (p1[0], 0)], 'loss', None)
    g.text((p2[0] + 2.2, -8), '', size=10)
    g.drop(p1, 'P_1', 'Q_1'); g.drop(p2, 'P_2', 'Q_2'); g.dot(p1); g.dot(p2)
    g.text((80, 25), 'loss = (Q₁−Q₂)×P₁ (small)', size=11, anchor='middle'); g.arrow((70, 21), (p2[0]+2, 14))
    return figure(g)

@dia('pes-range', 'Price elasticity of supply (PES)', 't2-6',
     steps=['A straight supply curve that starts on the price axis is elastic (PES > 1).', 'One that starts at the origin is unit elastic (PES = 1) whatever its slope.', 'One that starts on the quantity axis is inelastic (PES < 1).', 'Vertical = perfectly inelastic; horizontal = perfectly elastic.'],
     explain='PES measures how responsive quantity supplied is to a change in price. It is higher when firms have spare capacity, hold stocks, can move factors of production easily (factor mobility), have a longer time period to adjust, and produce manufactured goods rather than agricultural or mineral goods (which take time to grow or extract).',
     watch='For straight lines, where the line meets an axis decides PES, not how steep it is.')
def _():
    g = G()
    g.line((0, 30), (70, 99), 's', 'PES > 1', off=(4, 0))
    g.line((0, 0), (90, 90), 's', 'PES = 1', off=(4, 4))
    g.line((30, 0), (95, 70), 's', 'PES < 1', off=(-20, -12))
    g.line((15, 5), (15, 92), 'k', 'PES = 0', off=(-16, -8), dash=True)
    g.line((5, 15), (95, 15), 'k', 'PES = ∞', off=(-46, -10), dash=True)
    return figure(g)

# ---------------- 2.7 Government intervention ----------------
@dia('price-ceiling', 'Maximum price (price ceiling)', 't2-7',
     steps=['Draw D and S with equilibrium Pe, Qe.', 'Draw a horizontal line Pmax below Pe.', 'Read off Qs (on S) and Qd (on D) at Pmax: the gap is the shortage.', 'HL: shade the welfare changes (consumer surplus, producer surplus, welfare loss).'],
     explain='A maximum price is set below equilibrium to make a necessity affordable (rent controls, food staples, fuel). Quantity supplied contracts to Qs and quantity demanded extends to Qd, causing a shortage (Qd − Qs). Consequences: queues and waiting lists, non-price rationing (first come first served, favouritism), parallel (black) markets, lower quality, and underallocation of resources. HL: consumers who still buy gain area from producers, producer surplus falls, and the units between Qs and Qe are lost entirely: a welfare (deadweight) loss.',
     watch='A ceiling above equilibrium has no effect; it must be below Pe to bind.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D'); S = g.line(*S0, 's', 'S')
    E = meet(D, S); y = 32
    qs, qd = S.x_at(y), D.x_at(y)
    g.area([(qs, y), (qs, D.y_at(qs)), E], 'dwl', 'WL', at=(qs+5.5, 50))
    g.drop(E, 'P_e', 'Q_e'); g.hline(y, 'g', 'P_max', 0, 96, off=(-34, -10)); g.dot(E)
    g.drop((qs, y), None, 'Q_s', 'x'); g.drop((qd, y), None, 'Q_d', 'x')
    g.brace(qs, qd, y, 'shortage', below=True)
    g.drop((qs, D.y_at(qs)), 'P_b', None, 'y')
    return figure(g)

@dia('price-floor', 'Minimum price (price floor) with government buying the surplus', 't2-7',
     steps=['Draw D and S with equilibrium Pe, Qe.', 'Draw Pmin above Pe.', 'Quantity demanded contracts to Qd and quantity supplied extends to Qs: the gap is the surplus.', 'HL: if the government buys the surplus, its spending is Pmin × (Qs − Qd), the shaded rectangle.'],
     explain='Minimum prices protect producers\' incomes (agricultural price supports such as the EU\'s former intervention buying) or reduce consumption of a demerit good (minimum unit pricing of alcohol in Scotland). They create a surplus. The government may buy and store or destroy it (opportunity cost of public funds), sell it abroad (dumping, which hurts farmers in other countries), or pay farmers to produce less. Consumers pay more and buy less; inefficient producers are protected, reducing the incentive to cut costs.',
     watch='Floor above equilibrium. Without government purchase the surplus is unsold stock.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D'); S = g.line(*S0, 's', 'S')
    E = meet(D, S); y = 68
    qd, qs = D.x_at(y), S.x_at(y)
    g.area([(qd, 0), (qd, y), (qs, y), (qs, 0)], 'gov', 'gov. spending', at=((qd+qs)/2, 22))
    g.drop(E, 'P_e', 'Q_e'); g.hline(y, 'g', 'P_min', 0, 96, off=(-34, -10)); g.dot(E)
    g.drop((qd, y), None, 'Q_d', 'x'); g.drop((qs, y), None, 'Q_s', 'x')
    g.brace(qd, qs, y, 'surplus', below=False)
    return figure(g)

@dia('min-wage', 'National minimum wage in the labour market', 't2-7',
     steps=['Label axes Wage rate (W) and Quantity of labour (L).', 'Draw labour demand (DL, from firms) and labour supply (SL, from workers).', 'Draw Wmin above the equilibrium wage.', 'Show labour supplied (Ls) and demanded (Ld) at Wmin; the gap is unemployment (surplus of labour).'],
     explain='A minimum wage raises the incomes of low-paid workers who keep their jobs and can reduce poverty and in-work benefits, but at the higher wage firms employ fewer workers (Ld) while more people want to work (Ls). The surplus of labour is unemployment. Its size depends on the wage elasticity of labour demand and supply. In a market where firms have buying power (monopsony), a minimum wage may raise both pay and employment.',
     watch='The supply of labour comes from households, the demand from firms; do not swap them.')
def _():
    g = G('Quantity of labour', 'Wage rate'); D = g.line(*D0, 'd', 'D_L'); S = g.line(*S0, 's', 'S_L')
    E = meet(D, S); y = 66; ld, ls = D.x_at(y), S.x_at(y)
    g.drop(E, 'W_e', 'L_e'); g.hline(y, 'g', 'W_min', 0, 96, off=(-36, -10)); g.dot(E)
    g.drop((ld, y), None, 'L_d', 'x'); g.drop((ls, y), None, 'L_s', 'x')
    g.brace(ld, ls, y, 'unemployment', below=False)
    return figure(g)

@dia('tax-specific', 'Specific (per-unit) indirect tax: incidence and welfare', 't2-7',
     steps=['Draw D and S (= MC) with equilibrium P₁, Q₁.', 'Shift supply up by the amount of the tax to S + tax, parallel to S.', 'New equilibrium at Pc (price paid by consumers) and Q₂; drop down to S to find Pp (price received by producers).', 'Shade the tax revenue (Pc − Pp) × Q₂, split into the consumer and producer burden; shade the welfare loss triangle.'],
     explain='A specific tax is a fixed amount per unit (e.g. $2 per pack). The supply curve shifts vertically up by the tax. Consumers pay more (Pc > P₁), producers receive less (Pp < P₁), and quantity falls to Q₂. The government earns (Pc − Pp) × Q₂. Consumer burden = (Pc − P₁) × Q₂; producer burden = (P₁ − Pp) × Q₂. The units between Q₂ and Q₁ are no longer traded: a loss of social surplus (welfare loss) if there were no externalities to correct.',
     watch='The vertical distance between S and S + tax is the tax per unit and stays constant. The burden falls more on whichever side is less price elastic.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D'); S = g.line(*S0, 's', 'S')
    St = g.line((10, 34), (76, 100), 's', 'S + tax', off=(-50, 6))
    E1 = meet(D, S); E2 = meet(D, St); q2 = E2[0]; pp = S.y_at(q2)
    g.area([(0, E1[1]), (0, E2[1]), E2, (q2, E1[1])], 'cs', 'consumer burden', at=(q2/2, (E1[1]+E2[1])/2))
    g.area([(0, pp), (0, E1[1]), (q2, E1[1]), (q2, pp)], 'ps', 'producer burden', at=(q2/2, (E1[1]+pp)/2))
    g.area([E2, (q2, pp), E1], 'dwl', None)
    g.drop(E2, 'P_c', 'Q_2'); g.drop((q2, pp), 'P_p', None, 'y'); g.drop(E1, 'P_1', 'Q_1')
    g.dot(E1); g.dot(E2); g.dot((q2, pp))
    g.text((70, 46), 'welfare loss', size=11); g.arrow((64, 47), (48, 50))
    return figure(g)

@dia('tax-adval', 'Ad valorem (percentage) tax', 't2-7',
     steps=['Draw S and D.', 'Draw S + tax diverging from S: the gap widens as price rises because the tax is a percentage of the price.', 'Mark the new equilibrium and the price received by producers as for a specific tax.'],
     explain='An ad valorem tax, such as VAT or GST, is a percentage of the price, so the tax per unit is larger at higher prices. The new supply curve pivots upward rather than shifting in parallel. Analysis of incidence, revenue and welfare loss is the same as for a specific tax.',
     watch='The curves start together near the origin and spread apart.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D'); S = g.line((0, 5), (90, 85), 's', 'S')
    St = g.line((0, 6), (66, 99), 's', 'S + tax', off=(-52, 4))
    E1 = meet(D, S); E2 = meet(D, St); pp = S.y_at(E2[0])
    g.drop(E1, 'P_1', 'Q_1'); g.drop(E2, 'P_c', 'Q_2'); g.drop((E2[0], pp), 'P_p', None, 'y')
    g.dot(E1); g.dot(E2); g.dot((E2[0], pp))
    return figure(g)

@dia('tax-incidence', 'Tax incidence depends on PED and PES', 't2-7', hl=True,
     steps=['Draw two panels with the same tax per unit.', 'Left: inelastic (steep) demand — consumer burden is large.', 'Right: elastic (flat) demand — producer burden is large.'],
     explain='When demand is more price inelastic than supply, firms can pass most of the tax on to consumers in higher prices (tobacco, petrol, alcohol). When demand is more elastic than supply, consumers switch away, so producers absorb most of the tax. The more inelastic side of the market always bears the larger share. Taxing inelastic goods raises more revenue but does less to cut consumption.',
     watch='Use the same vertical tax gap in both panels so the comparison is fair.')
def _():
    out = []
    for title, Dl in [('Inelastic demand', ((38, 95), (62, 5))), ('Elastic demand', ((0, 68), (100, 36)))]:
        g = G(title=title, w=300); D = g.line(*Dl, 'd', 'D', off=(-6, -12) if title[0] == 'E' else (4, 0))
        S = g.line((5, 10), (95, 82), 's', 'S'); St = S.shifted(0, 24); g.line(St.p1, (St.x_at(98), 98), 's', 'S+t', off=(-34, 2))
        E1 = meet(D, S); E2 = meet(D, St); pp = S.y_at(E2[0])
        g.area([(0, E1[1]), (0, E2[1]), E2, (E2[0], E1[1])], 'cs')
        g.area([(0, pp), (0, E1[1]), (E2[0], E1[1]), (E2[0], pp)], 'ps')
        g.drop(E2, 'P_c', 'Q_2'); g.drop((E2[0], pp), 'P_p', None, 'y'); g.drop(E1, 'P_1', None, 'y'); g.dot(E1); g.dot(E2)
        out.append(g)
    return figure(*out)

@dia('subsidy', 'Producer subsidy: effects and welfare', 't2-7',
     steps=['Draw D and S with equilibrium P₁, Q₁.', 'Shift supply down by the subsidy per unit to S − subsidy.', 'New equilibrium: consumers pay Pc, quantity Q₂; producers receive Pp (read off the original S at Q₂).', 'Shade government spending (Pp − Pc) × Q₂ and the welfare loss triangle from overallocation.'],
     explain='A subsidy is a payment from the government to producers per unit of output. It lowers costs, shifting S down by the subsidy. Consumers pay less (Pc), producers receive more (Pp), and output rises from Q₁ to Q₂. Government cost = subsidy per unit × Q₂. Used to make necessities cheaper, support farmers\' incomes, help firms compete internationally, or encourage goods with positive externalities (solar panels, EVs). Without an externality the extra output beyond Q₁ is overallocation, creating a welfare loss.',
     watch='Producers receive Pp, which is above P₁; the gap Pp − Pc is the subsidy.')
def _():
    g = G(); D = g.line(*D0, 'd', 'D'); S = g.line(*S0, 's', 'S')
    Ss = g.line((34, 10), (100, 76), 's', 'S − subsidy', off=(-76, 12))
    E1 = meet(D, S); E2 = meet(D, Ss); q2 = E2[0]; pp = S.y_at(q2)
    g.area([(0, E2[1]), (0, pp), (q2, pp), E2], 'gov', 'government spending', at=(q2/2, (pp+E2[1])/2))
    g.area([E1, (q2, pp), E2], 'dwl')
    g.drop((q2, pp), 'P_p', None, 'y'); g.drop(E2, 'P_c', 'Q_2'); g.drop(E1, 'P_1', 'Q_1')
    g.dot(E1); g.dot(E2); g.dot((q2, pp))
    return figure(g)

# ---------------- 2.8 Externalities ----------------
def _ext(kind):
    g = G()
    if kind == 'np':
        D = g.line(*D0, 'd', 'D = MPB = MSB'); S = g.line(*S0, 's', 'S = MPC'); Sx = g.line((0, 22), (74, 96), 's', 'MSC', off=(-6, -10))
        Em = meet(D, S); Eo = meet(D, Sx)
        g.area([Eo, (Em[0], Sx.y_at(Em[0])), Em], 'dwl', None)
        g.drop(Em, 'P_m', 'Q_m'); g.drop(Eo, 'P_opt', 'Q_opt'); g.dot(Em); g.dot(Eo)
        g.text((76, 70), 'welfare loss', size=11); g.arrow((70, 66), (52, 58))
    elif kind == 'nc':
        S = g.line(*S0, 's', 'S = MPC = MSC'); D = g.line(*D0, 'd', 'MPB', off=(-8, -12)); Dx = g.line((0, 78), (78, 0), 'd', 'MSB', off=(-6, 12))
        Em = meet(D, S); Eo = meet(Dx, S)
        g.area([Eo, (Em[0], Dx.y_at(Em[0])), Em], 'dwl', None)
        g.drop(Em, 'P_m', 'Q_m'); g.drop(Eo, 'P_opt', 'Q_opt'); g.dot(Em); g.dot(Eo)
        g.text((76, 32), 'welfare loss', size=11); g.arrow((70, 34), (52, 44))
    elif kind == 'pp':
        D = g.line(*D0, 'd', 'D = MPB = MSB'); S = g.line(*S0, 's', 'S = MPC'); Sx = g.line((22, 0), (96, 74), 's', 'MSC', off=(-6, 12))
        Em = meet(D, S); Eo = meet(D, Sx)
        g.area([Em, (Em[0], Sx.y_at(Em[0])), Eo], 'dwl', None)
        g.drop(Em, 'P_m', 'Q_m'); g.drop(Eo, 'P_opt', 'Q_opt'); g.dot(Em); g.dot(Eo)
        g.text((80, 32), 'welfare loss', size=11); g.arrow((74, 34), (56, 40))
    else:
        S = g.line(*S0, 's', 'S = MPC = MSC'); D = g.line(*D0, 'd', 'MPB', off=(-6, 12)); Dx = g.line((22, 100), (100, 22), 'd', 'MSB', off=(-6, -12))
        Em = meet(D, S); Eo = meet(Dx, S)
        g.area([Em, (Em[0], Dx.y_at(Em[0])), Eo], 'dwl', None)
        g.drop(Em, 'P_m', 'Q_m'); g.drop(Eo, 'P_opt', 'Q_opt'); g.dot(Em); g.dot(Eo)
        g.text((84, 34), 'welfare loss', size=11); g.arrow((78, 38), (58, 50))
    return figure(g)

@dia('ext-neg-prod', 'Negative production externality', 't2-8',
     steps=['Draw D = MPB = MSB and S = MPC.', 'Draw MSC above MPC: the vertical gap is the external cost per unit.', 'Mark the market outcome Qm (MPB = MPC) and the social optimum Qopt (MSB = MSC).', 'Shade the welfare loss triangle between MSC and MSB from Qopt to Qm.'],
     explain='Producers ignore the costs they impose on third parties (pollution from factories, power stations, intensive farming), so MSC > MPC. The market produces Qm, more than the socially optimal Qopt, at too low a price: overallocation of resources. For each unit between Qopt and Qm, MSC > MSB, so society loses the shaded welfare loss. Solutions: Pigouvian (carbon) taxes, tradable permits, regulation, and international agreements.',
     watch='The welfare loss triangle points towards Qopt and has its vertical side at Qm.')
def _(): return _ext('np')

@dia('ext-neg-cons', 'Negative consumption externality', 't2-8',
     steps=['Draw S = MPC = MSC and MPB.', 'Draw MSB below MPB: the gap is the external cost of consumption.', 'Mark Qm (MPB = MPC) and Qopt (MSB = MSC).', 'Shade the welfare loss between MSC and MSB from Qopt to Qm.'],
     explain='Consumption that harms others (smoking, alcohol, driving in congestion, loud music) means MSB < MPB. Consumers buy Qm, more than the optimum Qopt: overconsumption. Demerit goods are often analysed this way, combined with imperfect information about personal harm. Policies: indirect taxes, legislation and bans, advertising restrictions, education, nudges.',
     watch='It is the demand-side curve that splits; supply is MPC = MSC.')
def _(): return _ext('nc')

@dia('ext-pos-prod', 'Positive production externality', 't2-8',
     steps=['Draw D = MPB = MSB and S = MPC.', 'Draw MSC below MPC: the gap is the external benefit of production.', 'Mark Qm and Qopt (larger).', 'Shade the welfare loss triangle between Qm and Qopt.'],
     explain='Production that benefits third parties (firm training that workers take elsewhere, R&D spillovers, bees from a honey farm pollinating orchards) means MSC < MPC. The market produces too little (Qm < Qopt): underallocation. Policies: subsidies, direct provision, tax credits for R&D.',
     watch='The welfare loss lies to the right of Qm.')
def _(): return _ext('pp')

@dia('ext-pos-cons', 'Positive consumption externality (merit goods)', 't2-8',
     steps=['Draw S = MPC = MSC and D = MPB.', 'Draw MSB above MPB: the gap is the external benefit of consumption.', 'Mark Qm and Qopt.', 'Shade the welfare loss between Qm and Qopt.'],
     explain='Education, vaccinations and healthcare benefit people other than the consumer (a more productive workforce, herd immunity), so MSB > MPB. Consumers also often underestimate private benefits (imperfect information). The market under-consumes: Qm < Qopt. Policies: subsidies, direct government provision, legislation (compulsory schooling), advertising and nudges.',
     watch='Merit goods are under-consumed because of positive externalities and imperfect information, not only because they are expensive.')
def _(): return _ext('pc')

@dia('pigou-tax', 'Pigouvian (carbon) tax on a negative production externality', 't2-8',
     steps=['Draw MPB = MSB, MPC and MSC with Qm > Qopt.', 'Set the tax equal to the external cost per unit, so MPC + tax = MSC.', 'Output falls to Qopt; price rises to Popt; the welfare loss is eliminated.'],
     explain='A tax equal to the marginal external cost internalises the externality: firms now pay the full social cost. Advantages: market-based, raises revenue, gives an incentive to cut pollution in the cheapest way. Problems: measuring the external cost in money is hard; demand for many polluting goods is price inelastic so output may fall little; regressive effects on low-income households; firms may relocate (carbon leakage); political resistance.',
     watch='The tax shifts MPC up to MSC; draw it on the same curve.')
def _():
    g = G(); D = g.line(*D0, 'd', 'MPB = MSB'); S = g.line(*S0, 's', 'MPC'); Sx = g.line((0, 22), (74, 96), 's', 'MSC = MPC + tax', off=(-60, -12))
    Em = meet(D, S); Eo = meet(D, Sx)
    g.drop(Em, 'P_m', 'Q_m'); g.drop(Eo, 'P_opt', 'Q_opt'); g.dot(Em); g.dot(Eo)
    g.arrow((50, 56), (50, 68)); g.text((60, 63), 'tax', size=11)
    return figure(g)

@dia('subsidy-merit', 'Subsidy to correct a positive consumption externality', 't2-8',
     steps=['Draw MPB, MSB (above) and S = MPC.', 'Draw S − subsidy shifted down by the external benefit.', 'The new equilibrium is at Qopt, where MPB meets S − subsidy.'],
     explain='Subsidising a merit good (vaccines, solar panels, public transport fares) lowers its price and raises consumption to the social optimum. The government must fund the subsidy (opportunity cost), choose the right size (external benefits are hard to measure), and may find that firms simply keep the subsidy if supply is inelastic.',
     watch='Quantity rises to Qopt; the price consumers pay falls.')
def _():
    g = G(); S = g.line(*S0, 's', 'S = MPC'); D = g.line(*D0, 'd', 'MPB', off=(-6, 12)); Dx = g.line((22, 100), (100, 22), 'd', 'MSB', off=(-6, -12))
    Ss = g.line((22, 0), (100, 78), 's', 'S − subsidy', off=(-62, 14))
    Em = meet(D, S); Eo = meet(Dx, S); Ec = meet(D, Ss)
    g.drop(Em, 'P_m', 'Q_m'); g.drop(Ec, 'P_c', 'Q_opt'); g.dot(Em); g.dot(Ec); g.dot(Eo, 'MSB = MSC', off=(-80, -8))
    return figure(g)

@dia('permits', 'Tradable permits (cap and trade)', 't2-8',
     steps=['Label axes Price of permits and Quantity of permits (or pollution).', 'Draw a vertical supply of permits S fixed by the government (the cap).', 'Draw the demand for permits D₁; show demand rising to D₂ as the economy grows, raising the permit price.', 'Show the government reducing the cap from S₁ to S₂ over time.'],
     explain='The authority sets a cap on total emissions and issues (or auctions) permits; firms that cut pollution cheaply sell spare permits to firms for which cutting is costly. The pollution target is met at the lowest total cost, and the permit price gives a continuing incentive to invest in clean technology. The EU Emissions Trading System is the largest example. Problems: setting the cap too high (permit prices collapsed after 2008), lobbying for free allocations, monitoring costs, carbon leakage.',
     watch='Supply of permits is perfectly inelastic: it is a policy choice, not a market response.')
def _():
    g = G('Quantity of permits', 'Price of permits')
    g.line((60, 5), (60, 95), 's', 'S_1'); g.line((42, 5), (42, 95), 's', 'S_2', off=(-20, -6), dash=True)
    D1 = g.line((0, 70), (100, 10), 'd', 'D_1'); D2 = g.line((0, 92), (100, 32), 'd', 'D_2')
    for D, Sx, l in [(D1, 60, 'P_1'), (D2, 60, 'P_2'), (D1, 42, 'P_3')]:
        p = (Sx, D.y_at(Sx)); g.drop(p, l, None, 'y'); g.dot(p)
    g.xtick(60, 'cap₁'); g.xtick(42, 'cap₂')
    return figure(g)
