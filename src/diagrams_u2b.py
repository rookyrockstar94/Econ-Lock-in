from diagram_engine import *
from diagrams_reg import dia

# cost model in plot units: AVC = 60 - 1.6q + 0.016q^2, FC = 600
AVC = lambda q: 60 - 1.6*q + 0.016*q*q
MC = lambda q: 60 - 3.2*q + 0.048*q*q
AFC = lambda q: 600/q
ATC = lambda q: AVC(q) + AFC(q)
def solve(f, lo, hi):
    for _ in range(80):
        m = (lo+hi)/2
        if (f(lo) > 0) == (f(m) > 0): lo = m
        else: hi = m
    return (lo+hi)/2
QATC = solve(lambda q: MC(q) - ATC(q), 40, 80)  # min ATC
def costs(g, afc=False, avc=True, x1=88):
    g.fn(MC, 8, x1, 'c', 'MC', off=(-8, -10))
    g.fn(ATC, 9, 96, 'c', 'ATC', off=(-6, -12))
    if avc: g.fn(AVC, 5, 96, 'c', 'AVC', off=(-4, 4), dash=False)
    if afc: g.fn(AFC, 7, 96, 'k', 'AFC', off=(-10, -12))

@dia('cost-curves', 'Short-run cost curves', 't2-11', hl=True,
     steps=['Label axes Costs/revenue and Output (Q).', 'Draw MC as a "tick" shape: falling at first, then rising.', 'Draw AVC and ATC as U shapes, with ATC above AVC; the gap between them is AFC, which narrows as output rises.', 'Make sure MC cuts AVC and then ATC at their lowest points.'],
     explain='In the short run at least one factor is fixed. MC first falls because of increasing marginal returns, then rises because of the law of diminishing marginal returns: adding more of a variable factor to a fixed factor eventually adds less and less output. When MC is below an average it pulls the average down; when above, it pulls it up. So MC passes through the minimum of AVC and ATC. AFC = FC/Q falls continuously as fixed costs are spread over more units.',
     watch='The most common slip is MC crossing ATC away from its minimum point.')
def _():
    g = G('Output (Q)', 'Costs'); costs(g, afc=True)
    q = solve(lambda q: MC(q) - AVC(q), 30, 70); g.dot((q, AVC(q))); g.dot((QATC, ATC(QATC)))
    return figure(g)

@dia('lrac', 'Long-run average cost: economies and diseconomies of scale', 't2-11', hl=True,
     steps=['Draw a U-shaped LRAC (flatter than short-run AC).', 'Label the falling part "economies of scale" and the rising part "diseconomies of scale".', 'Mark the minimum efficient scale (MES): the lowest output at which LRAC is minimised.', 'Optionally sketch short-run AC curves tangent to LRAC.'],
     explain='In the long run all factors are variable. Economies of scale (falling LRAC) come from specialisation and division of labour, technical economies (bigger machines, the container principle), bulk buying, cheaper finance, marketing spread over more output and risk-bearing through diversification. Diseconomies (rising LRAC) come from coordination and communication problems, lower worker motivation and slower decisions in very large organisations.',
     watch='Economies of scale relate to the long run; diminishing returns to the short run. Do not mix them up.')
def _():
    g = G('Output (Q)', 'Costs')
    L = g.curve([(5, 85), (20, 52), (40, 34), (55, 30), (70, 33), (88, 50), (97, 64)], 'c', 'LRAC', off=(-12, -12))
    for c, w in [(14, 12), (40, 13), (78, 12)]:
        y0 = L.y_at(c); g.curve([(c-w, y0+18), (c-w/2, y0+5), (c, y0), (c+w/2, y0+5), (c+w, y0+18)], 'c', None, dash=True)
    g.drop((55, 30), None, 'MES', 'x')
    g.text((22, 22), 'economies of scale', size=11, italic=True); g.text((80, 22), 'diseconomies', size=11, italic=True)
    return figure(g)

@dia('revenue-curves', 'Revenue curves: perfect vs imperfect competition', 't2-11', hl=True,
     steps=['Left (price taker): one horizontal line labelled P = AR = MR = D at the market price.', 'Right (price maker): a downward AR = D line and an MR line twice as steep, starting at the same price intercept and meeting the quantity axis halfway.'],
     explain='A perfectly competitive firm can sell any amount at the market price, so every extra unit adds the same revenue: P = AR = MR. A firm with market power must cut price to sell more, so MR is below AR. With linear demand, MR falls twice as fast. Total revenue is maximised where MR = 0, which is where PED = 1 on the demand curve.',
     watch='MR crosses the quantity axis at half the quantity where AR does.')
def _():
    a = G('Output', 'Price', title='Perfect competition', w=300); a.hline(50, 'd', 'P = AR = MR', 0, 80, off=(-40, -12))
    b = G('Output', 'Price', title='Imperfect competition', w=300)
    b.line((0, 90), (90, 0), 'd', 'AR = D', off=(-36, -8)); b.line((0, 90), (45, 0), 'm', 'MR', off=(2, -6))
    b.xtick(45, 'MR = 0'); b.xtick(90, '')
    return figure(a, b)

def _pc(P, title_firm='Firm', loss=False, shutdown=False, show_industry=True):
    ind = G('Quantity', 'Price', title='Industry', w=250); ind.R = 46
    D = ind.line((5, 92), (92, 5), 'd', 'D', off=(-12, -12)); ix = D.x_at(P)
    S = ind.line((ix - min(ix, P) + 3, P - min(ix, P) + 3), (ix + 40, P + 40), 's', 'S')
    ind.drop((ix, P), 'P_e', 'Q_e'); ind.dot((ix, P))
    f = G('Output (q)', 'Costs/revenue', title=title_firm, w=360); costs(f, avc=(loss or shutdown))
    f.hline(P, 'd', 'P = AR = MR', 0, 99, off=(-74, -10))
    q = solve(lambda q: MC(q) - P, 34, 99)
    c = ATC(q)
    if c < P - 0.5: f.area([(0, c), (0, P), (q, P), (q, c)], 'prof', 'abnormal profit', at=(q/2, (P+c)/2))
    elif c > P + 0.5: f.area([(0, P), (0, c), (q, c), (q, P)], 'loss', 'loss', at=(q/2, (P+c)/2))
    f.drop((q, P), None, 'q^*', 'x'); f.dot((q, P))
    if abs(c - P) > 0.5: f.drop((q, c), 'ATC', None, 'y')
    return figure(ind, f)

@dia('pc-sr-profit', 'Perfect competition: short-run abnormal profit', 't2-11', hl=True,
     steps=['Draw the industry diagram (D and S) beside the firm diagram, with the market price carried across.', 'In the firm diagram the price line is P = AR = MR.', 'Find output q* where MC = MR (MC rising).', 'Read ATC at q*; profit per unit is P − ATC, and abnormal profit is the shaded rectangle (P − ATC) × q*.'],
     explain='Firms are price takers. Each produces where MC = MR. If the price is above ATC at that output, the firm earns abnormal (supernormal) profit. Because there are no barriers to entry and information is perfect, new firms are attracted in; industry supply shifts right and the price falls until only normal profit remains.',
     watch='Use small q for the firm and large Q for the industry.')
def _(): return _pc(45)

@dia('pc-sr-loss', 'Perfect competition: short-run loss', 't2-11', hl=True,
     steps=['Draw the industry and firm diagrams with a market price below the minimum of ATC but above the minimum of AVC.', 'Produce at MC = MR.', 'The loss is (ATC − P) × q*.'],
     explain='When price is below ATC the firm makes a loss but keeps producing in the short run as long as price covers average variable cost (P ≥ AVC): revenue then covers all variable costs and some of the fixed costs, which must be paid anyway. In the long run loss-making firms leave, industry supply shifts left and the price rises back to the minimum of ATC.',
     watch='Short-run shut-down price = minimum AVC; long-run break-even price = minimum ATC.')
def _(): return _pc(26, loss=True)

@dia('pc-lr', 'Perfect competition: long-run equilibrium', 't2-11', hl=True,
     steps=['Draw the firm\'s MC and ATC.', 'Draw the price line tangent to the minimum of ATC.', 'MC = MR = AR = ATC at q*: normal profit only.'],
     explain='In long-run equilibrium P = minimum ATC, so firms earn normal profit. The outcome is allocatively efficient (P = MC: the value consumers place on the last unit equals its cost) and productively efficient (production at minimum ATC). Perfect competition is the benchmark against which other market structures are judged.',
     watch='Both efficiency conditions should be written out: P = MC and production at minimum ATC.')
def _(): return _pc(ATC(QATC))

@dia('pc-shutdown', 'Short-run shut-down and break-even prices', 't2-11', hl=True,
     steps=['Draw MC, ATC and AVC.', 'Mark the break-even price at minimum ATC and the shut-down price at minimum AVC.', 'The firm\'s short-run supply curve is its MC curve above minimum AVC.'],
     explain='Below the shut-down price the firm cannot even cover its variable costs, so producing nothing (losing only fixed costs) is better. Between the shut-down and break-even prices it produces at a loss in the short run. This is why the supply curve of a competitive firm is the part of its MC curve above AVC.',
     watch='Label which point is which; examiners look for this distinction.')
def _():
    g = G('Output (q)', 'Costs/revenue'); costs(g)
    qa = solve(lambda q: MC(q) - AVC(q), 30, 70)
    g.hline(ATC(QATC), 'd', 'break-even price', 0, QATC, off=(4, -10), dash=True); g.hline(AVC(qa), 'd', 'shut-down price', 0, qa, off=(4, 12), dash=True)
    g.dot((QATC, ATC(QATC))); g.dot((qa, AVC(qa)))
    return figure(g)

AR = lambda q: 100 - 0.9*q; MR = lambda q: 100 - 1.8*q
@dia('monopoly', 'Monopoly: profit maximisation and abnormal profit', 't2-11', hl=True,
     steps=['Draw AR = D sloping down and MR twice as steep.', 'Add MC and ATC.', 'Find Qm where MC = MR; go up to AR for the price Pm.', 'Read ATC at Qm; abnormal profit = (Pm − ATC) × Qm.'],
     explain='A monopolist is the only seller, with high barriers to entry (economies of scale, legal barriers such as patents and licences, control of resources, brand loyalty, anti-competitive behaviour). It is a price maker but faces the market demand curve. It maximises profit where MC = MR and can keep abnormal profit in the long run because entry is blocked. It operates on the elastic part of demand (MR > 0).',
     watch='The price is read off the AR curve, not where MC meets MR.')
def _():
    g = G('Output (Q)', 'Costs/revenue')
    g.line((0, 100), (100, 10), 'd', 'AR = D', off=(-40, -10)); g.line((0, 100), (55.6, 0), 'm', 'MR', off=(2, -8))
    costs(g, avc=False)
    q = solve(lambda q: MC(q) - MR(q), 34, 55); p = AR(q); c = ATC(q)
    g.area([(0, c), (0, p), (q, p), (q, c)], 'prof', 'abnormal profit', at=(q/2, (p+c)/2))
    g.drop((q, p), 'P_m', 'Q_m'); g.drop((q, c), 'ATC', None, 'y'); g.dot((q, p)); g.dot((q, MR(q)))
    return figure(g)

@dia('monopoly-welfare', 'Monopoly vs perfect competition: welfare loss', 't2-11', hl=True,
     steps=['Draw D = AR, MR and MC (as the competitive industry\'s supply curve).', 'Competitive outcome: Pc, Qc where MC = D.', 'Monopoly outcome: Qm where MC = MR, price Pm on D.', 'Shade the welfare loss triangle between Qm and Qc, and show consumer surplus transferred to the monopolist.'],
     explain='Compared with perfect competition (with the same costs), a monopoly restricts output and charges a higher price. P > MC at Qm, so the monopoly is allocatively inefficient: units society values above their cost are not produced. Part of consumer surplus becomes producer surplus and the triangle is lost altogether. Counter-arguments: economies of scale may give the monopolist much lower costs (natural monopoly), and abnormal profits can fund R&D and innovation (dynamic efficiency).',
     watch='Assume the same MC for both structures, or the comparison is not valid.')
def _():
    g = G('Output (Q)', 'Price'); D = g.line((0, 92), (92, 0), 'd', 'D = AR', off=(-44, -8))
    M = g.line((0, 92), (46, 0), 'm', 'MR', off=(2, -8)); C = g.line((0, 15), (96, 75), 'c', 'MC = S', off=(-46, -12))
    Ec = meet(D, C); qm = meet(M, C)[0]; pm = D.y_at(qm)
    g.area([(qm, pm), (qm, C.y_at(qm)), Ec], 'dwl', 'WL', at=(qm + 6, (pm + C.y_at(qm))/2 + 2))
    g.area([(0, Ec[1]), (0, pm), (qm, pm), (qm, Ec[1])], 'prof', 'transfer', at=(qm/2, (pm+Ec[1])/2))
    g.drop((qm, pm), 'P_m', 'Q_m'); g.drop(Ec, 'P_c', 'Q_c'); g.dot((qm, pm)); g.dot(Ec)
    return figure(g)

@dia('natural-monopoly', 'Natural monopoly and price regulation', 't2-11', hl=True,
     steps=['Draw LRAC falling across the whole range of market demand, with LRMC below it.', 'Draw D = AR crossing LRAC while it is still falling.', 'Mark the unregulated outcome (MC = MR), the average-cost price (P = AC: normal profit) and the marginal-cost price (P = MC: allocatively efficient but a loss).'],
     explain='When economies of scale are so large that one firm can supply the whole market at lower average cost than two or more firms (water, rail track, electricity grids), the industry is a natural monopoly. Breaking it up would raise costs. Governments regulate it instead: marginal-cost pricing is allocatively efficient but the firm makes a loss and needs a subsidy; average-cost pricing lets the firm break even. Nationalisation is another option.',
     watch='LRAC must still be falling where it meets demand.')
def _():
    g = G('Output (Q)', 'Costs/revenue')
    L = g.curve([(6, 92), (15, 62), (30, 44), (50, 34), (75, 28), (98, 25)], 'c', 'LRAC', off=(-34, -12))
    Mc = g.curve([(5, 62), (14, 38), (28, 22), (50, 16), (75, 13), (98, 11)], 'c', 'LRMC', off=(-36, 12))
    D = g.line((0, 85), (85, 0), 'd', 'D = AR', off=(-48, -6))
    pac = cmeet(D, L, 30, 80); pmc = cmeet(D, Mc, 40, 95)
    g.drop(pac, 'P_AC', 'Q_AC'); g.drop(pmc, 'P_MC', 'Q_MC'); g.dot(pac); g.dot(pmc)
    return figure(g)

TQ = 45; TP = ATC(TQ); TS = -1.6 + 0.032*TQ - 600/TQ**2
@dia('monopolistic-comp', 'Monopolistic competition: short run and long run', 't2-11', hl=True,
     steps=['Short run: draw a downward AR (fairly elastic, many substitutes) with MR, MC and ATC; at MC = MR price is above ATC, so abnormal profit.', 'Long run: new firms enter, each firm\'s demand falls and becomes more elastic until AR is tangent to ATC at the output where MC = MR.', 'Long run: P = ATC, normal profit only.'],
     explain='Many firms sell differentiated products (restaurants, hairdressers, clothing brands) with low barriers to entry. Each has a little price-setting power because of product differentiation, so demand slopes down. Short-run abnormal profit attracts entrants until only normal profit remains. Long-run outcome: neither allocatively (P > MC) nor productively efficient (output is below the minimum of ATC: excess capacity). Consumers gain variety and choice.',
     watch='In the long-run diagram AR just touches ATC at one point, directly above MC = MR.')
def _():
    a = G('Output (q)', 'Costs/revenue', title='Short run', w=330)
    b = G('Output (q)', 'Costs/revenue', title='Long run', w=330)
    for g, up in [(a, 12), (b, 0)]:
        ar = lambda q: TP + up + TS*(q-TQ); mr = lambda q: TP + up - TS*TQ + 2*TS*q
        g.fn(ar, 0, 95, 'd', 'AR = D', off=(-46, -10)); g.fn(mr, 0, 70, 'm', 'MR', off=(2, -4))
        costs(g, avc=False)
        q = solve(lambda q: MC(q) - mr(q), 30, 70); p = ar(q); c = ATC(q)
        if up: g.area([(0, c), (0, p), (q, p), (q, c)], 'prof', 'profit', at=(q/2, (p+c)/2))
        g.drop((q, p), 'P', 'q'); g.dot((q, p))
    return figure(a, b)

@dia('kinked-demand', 'Kinked demand curve (oligopoly)', 't2-11', hl=True,
     steps=['Draw a demand curve with a kink at the current price P*: flat (elastic) above, steep (inelastic) below.', 'Draw the two matching MR segments, leaving a vertical gap (discontinuity) below the kink.', 'Show MC₁ and MC₂ both passing through the gap: price and output stay at P*, Q*.'],
     explain='If one oligopolist raises its price, rivals do not follow, so it loses many customers (elastic above the kink). If it cuts price, rivals match the cut, so it gains few customers (inelastic below). Either change reduces revenue, so prices are "sticky" and firms compete through non-price competition (advertising, branding, loyalty schemes, product development). Costs can change within the MR gap without changing price. Limitations: it explains why prices are stable but not how P* was set in the first place.',
     watch='The MR gap lies directly below the kink.')
def _():
    g = G('Output (Q)', 'Price'); k = (45, 58)
    g.line((0, 72), k, 'd'); g.line(k, (68, 0), 'd', 'D = AR', off=(-14, -20))
    g.line((0, 72), (45, 44), 'm'); g.line((45, 24), (57, 0), 'm', 'MR', off=(4, -8))
    g.line((45, 44), (45, 24), 'm', dash=True)
    g.curve([(20, 26), (35, 28), (45, 32), (60, 44), (72, 62)], 'c', 'MC_1', off=(2, -2))
    g.curve([(20, 36), (35, 37), (45, 40), (60, 52), (70, 68)], 'c', 'MC_2', off=(2, -2))
    g.drop(k, 'P^*', 'Q^*'); g.dot(k, 'kink')
    return figure(g)
