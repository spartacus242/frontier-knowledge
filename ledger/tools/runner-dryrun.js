// Dry run of the batch runner's control flow with stubbed agents. No network, no model, no tokens.
//
//   node ledger/tools/runner-dryrun.js            checks the newest runner in this folder
//   node ledger/tools/runner-dryrun.js <runner>   checks the one named
//
// Each scenario feeds the runner made-up agent answers and counts which agents it calls, so a change to the
// runner's flow (who is developed, who gets a second adversary, when the judge runs, when the rerun fires) shows
// up here before it costs anything. Scenarios G onward make an agent return nothing, or throw, and check that the
// runner says so in its return instead of going on as if it had an answer. It checks the flow only: the prompts are
// not read by anything, except that a prompt containing the text "undefined" fails, which catches a missing
// argument, and that two scenarios look for a phrase the prompt must carry. Exits non-zero on a failure.
const fs = require('fs')
const path = require('path')
const newest = () => fs.readdirSync(__dirname).filter(f => /^unasked-ledger-batch-sequential-v\d+\.js$/.test(f))
  .sort((a, b) => Number(a.match(/v(\d+)/)[1]) - Number(b.match(/v(\d+)/)[1])).map(f => path.join(__dirname, f)).pop()
const runnerPath = process.argv[2] || newest()
console.log('runner: ' + path.relative(process.cwd(), runnerPath))
const src = fs.readFileSync(runnerPath, 'utf8').replace(/^export const meta/m, 'const meta')
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
const body = new AsyncFunction('args', 'agent', 'parallel', 'pipeline', 'phase', 'log', 'budget', 'workflow', src)

const parallel = thunks => Promise.all(thunks.map(t => Promise.resolve().then(t).catch(() => null)))
const pipeline = (items, ...stages) => Promise.all(items.map(async (item, idx) => {
  let v = item
  try { for (const st of stages) v = await st(v, item, idx) } catch (e) { console.log('   stage threw:', e.message); return null }
  return v
}))

const METHODS = ['anomaly mining', 'presupposition inversion', 'cross-field transplant', 'new-instrument questions']
const ID = n => `UQ-20261203-${n}`
const eight = st => ['1', '2', '3', '4', '5', '6', '7', '8'].map(a => ({ attack: a, status: st }))
const adv = verdict => ({ statuses: eight(verdict === 'Rejected' ? 'Unresolved' : 'Resolved'), verdict, key_kill: '', disguise_queries_run: 8,
  depth_check: 'Pass', depth_object: 'x', attack4_grade: 'NONE', attack2_leg: 'NONE', ambition_challenge: '' })
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)

// cfg.dead maps an agent's label to how many of its attempts return nothing (2 means the retry fails too);
// cfg.throws lists labels whose agent throws; cfg.depthFail maps a candidate to the summary of a Gate 0 failure.
async function scenario(name, cfg, expect, also) {
  const calls = [], prompts = {}, attempts = {}
  const agent = async (prompt, opts) => {
    const label = opts.label
    calls.push(label)
    prompts[label] = prompt
    if (typeof prompt !== 'string' || prompt.includes('undefined')) { const i = String(prompt).indexOf('undefined'); throw new Error(`prompt for ${label} is not a clean string: …${String(prompt).slice(Math.max(0, i - 160), i + 40)}…`) }
    const base = label.replace(/:retry$/, '')
    attempts[base] = (attempts[base] || 0) + 1
    if ((cfg.throws || []).includes(base)) throw new Error('made-up failure in ' + base)
    if (attempts[base] <= ((cfg.dead || {})[base] || 0)) return null
    const [kind, id] = label.split(':')
    if (kind === 'draft') return { drafts: [{ key: id, source_method: 'm', domain: 'mathematics', headline: `H ${id}`, derivation: 'Seed: s. Move: m. Why: w.', motivating_gap: 'g', depth: 'd', test_sketch: 't', method_guess: 'computation; AI yes' }] }
    if (kind === 'rank') return { scored: Object.entries(cfg.scores).map(([key, a]) => ({ key, ambition: a < 0 ? 0 : a, if_yes: 'y', if_no: 'n', discarded: a < 0, discard_reason: '', triage: '' })), chosen: cfg.chosen }
    if (kind === 'develop' || kind === 'redevelop') return { candidates: [{ key: id, source_method: 'm', domain: 'mathematics', headline: 'changed', question: `Q ${id}`, alternatives: ['a', 'b'], motivating_gap: 'g', presuppositions: ['p'], answer_criterion: 'c', depth: 'd' }] }
    if (kind === 'research') {
      const fail = (cfg.depthFail || {})[id.slice(-2)]
      return { headline_novelty: 'High', under_asked: !!cfg.underAsked, novelty: (cfg.low || []).some(k => id.endsWith(k)) ? 'Low' : 'High', well_posed: true, asked_but_open: false, nearest_prior: 'p', query_count: fail ? 0 : 10,
        summary: fail || 's', depth_pass: !fail, depth_note: fail ? 'object test fails' : '', solving_method: 'Method: x', ai_progress: 'partly' }
    }
    if (kind === 'adversary1') return adv((cfg.a1 || {})[id.slice(-2)] || (cfg.a1 || {})[id.slice(-3)] || 'Provisional')
    if (kind === 'adversary2') return adv((cfg.a2 || {})[id.slice(-2)] || 'Provisional')
    if (kind === 'adversary3') return adv('Provisional')
    if (kind === 'judge' || kind === 'rejudge') {
      const st = (cfg.judge || {})[id.slice(-2)] || (cfg.judge || {})[id.slice(-3)] || 'Provisional'
      return { status: st, tier: 'Standard', ambition: 2, gate: st === 'Rejected' ? 'Gate 4' : 'Gate 5', one_line: 'o', routing_row: '', redevelop: !!(cfg.redevelop || []).includes(id.slice(-2)), redevelop_reason: 'r' }
    }
    throw new Error('unexpected label ' + label)
  }
  const args = { dir: '/tmp/x', repo: '/repo', area: 'mathematics', date: '20261203', dateIso: '2026-12-03', startId: 1, indexCount: 246, batch: '2026-12-03-1233', methods: cfg.methods || METHODS, supplied: cfg.supplied }
  let out, err
  try { out = await body(args, agent, parallel, pipeline, () => {}, m => console.log('   log:', m), { total: null }, null) } catch (e) { err = e }
  const count = k => calls.filter(l => l.split(':')[0] === k).length
  const got = err ? { error: true } : { drafts: count('draft'), develop: count('develop'), research: count('research'), adv1: count('adversary1'), adv2: count('adversary2'), adv3: count('adversary3'),
    judge: count('judge'), rejudge: count('rejudge'), redevelop: count('redevelop'), candidates: out.candidates.map(c => `${c.id}:${c.status}`).join(' ') }
  let ok = same(got, expect), why = ''
  if (ok && also) { why = also(out, prompts, err, calls) || ''; ok = !why }
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}\n   got      ${JSON.stringify(got)}${same(got, expect) ? '' : '\n   expected ' + JSON.stringify(expect)}${why ? '\n   ' + why : ''}${err ? '\n   error: ' + err.message.slice(0, 160) : ''}`)
  if (!ok) process.exitCode = 1
  return out
}

// What a clean run owes: nothing.
const owes = (out, want) => {
  const got = { noRecordIds: out.noRecordIds, adversaryOwedIds: out.adversaryOwedIds, noVerdictIds: out.noVerdictIds, rerunUndecided: out.rerunUndecided, rerunOwed: out.rerunOwed }
  const full = { noRecordIds: [], adversaryOwedIds: [], noVerdictIds: [], rerunUndecided: false, rerunOwed: [], ...want }
  return same(got, full) ? '' : `owed lists: got ${JSON.stringify(got)}, expected ${JSON.stringify(full)}`
}
const two = { D1: 2, D2: 2, D3: 1, D4: 1 }

;(async () => {
  // A. One survivor, one rejected by its first adversary: 2 judges in all (v23 used 3), no rerun.
  await scenario('A one survives, one killed by adversary 1',
    { scores: { D1: 2, D2: 3, D3: 1, D4: 2 }, chosen: ['D2', 'D1', 'D4'], a1: { '02': 'Rejected' }, judge: { '02': 'Rejected' } },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 2, adv3: 0, judge: 2, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Rejected` },
    a => (a.candidates[0].headline !== 'H D2' || a.methods.length !== 4 || a.drafts.length !== 4 || a.candidates[0].ai_progress !== 'partly') ? 'headline, methods or drafts not carried'
      : !same(a.equalisedIds, [ID('02')]) ? 'equalisedIds should name the candidate adversary 1 rejected' : owes(a, {}))
  // B. Both survive: the low-rate rerun fires on both.
  await scenario('B both survive, rerun fires',
    { scores: { D1: 2, D2: 2, D3: 2, D4: 2 }, chosen: ['D1', 'D2'] },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 2, adv3: 2, judge: 2, rejudge: 2, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Provisional` },
    (o, p) => !same(o.rerunIds, [ID('01'), ID('02')]) ? 'rerunIds should name both' : !p[`rejudge:${ID('01')}`].includes('-adversary-3.md') ? 'the second judge was not handed the third log' : owes(o, {}))
  // C. No draft scores 2 or more: nothing is developed.
  await scenario('C no draft scores 2 or more',
    { scores: { D1: 1, D2: 1, D3: 0, D4: -1 }, chosen: ['D1', 'D2'] },
    { drafts: 4, develop: 0, research: 0, adv1: 0, adv2: 0, adv3: 0, judge: 0, rejudge: 0, redevelop: 0, candidates: '' }, o => owes(o, {}))
  // D. Only one draft scores 2 or more; Gate 2 grades it Low; rejected; marked for re-development, which runs once.
  await scenario('D one developed, Gate 2 Low, re-developed once',
    { scores: { D1: 1, D2: 2, D3: 1, D4: 1 }, chosen: ['D2', 'D1'], low: ['01'], judge: { '01': 'Rejected', '01R': 'Provisional' }, redevelop: ['01'] },
    { drafts: 4, develop: 1, research: 2, adv1: 2, adv2: 2, adv3: 0, judge: 2, rejudge: 0, redevelop: 1, candidates: `${ID('01')}:Rejected ${ID('01R')}:Provisional` },
    o => !same(o.redevelopedIds, [ID('01R')]) || o.redevelopOwed.length ? 're-development not reported as run' : owes(o, {}))
  // E. A wrong methods argument stops the run before any agent is spent.
  await scenario('E two methods where four are needed', { scores: {}, chosen: [], methods: ['anomaly mining', 'limits'] }, { error: true },
    (o, p, err, calls) => calls.length ? 'an agent was called' : /args\.methods must be an array/.test(err.message) ? '' : 'stopped for another reason: ' + err.message)
  // F. Supplied headlines (the backtest path) skip drafting and are all developed, as in v23. The one below 2 is a
  //    Gate 3 (ambition) rejection, and it is not re-developed even when the judge marks it.
  await scenario('F supplied headlines, one below 2',
    { scores: { S1: 2, S2: 1 }, chosen: ['S1', 'S2'], supplied: [{ headline: 'h1' }, { headline: 'h2' }], methods: [], judge: { '02': 'Rejected' }, redevelop: ['02'] },
    { drafts: 0, develop: 2, research: 1, adv1: 1, adv2: 1, adv3: 0, judge: 2, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Rejected` }, o => owes(o, {}))

  // G. A researcher returns nothing twice: no adversary and no judge is spent on that candidate, and the rerun waits.
  await scenario('G a researcher returns nothing twice',
    { scores: two, chosen: ['D1', 'D2'], dead: { [`research:${ID('01')}`]: 2 } },
    { drafts: 4, develop: 2, research: 3, adv1: 1, adv2: 1, adv3: 0, judge: 1, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:null ${ID('02')}:Provisional` },
    o => owes(o, { noRecordIds: [ID('01')], noVerdictIds: [ID('01')], rerunUndecided: true }))
  // H. A researcher returns nothing once: the retry is used and the run goes on as in B.
  await scenario('H a researcher returns nothing once',
    { scores: two, chosen: ['D1', 'D2'], dead: { [`research:${ID('01')}`]: 1 } },
    { drafts: 4, develop: 2, research: 3, adv1: 2, adv2: 2, adv3: 2, judge: 2, rejudge: 2, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Provisional` }, o => owes(o, {}))
  // I. The only judge of a candidate (since v24 it is judged once, in Equalise) returns nothing once: it is asked again.
  await scenario('I the only judge of a candidate returns nothing once',
    { scores: two, chosen: ['D1', 'D2'], a1: { '02': 'Rejected' }, judge: { '02': 'Rejected' }, dead: { [`judge:${ID('02')}`]: 1 } },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 2, adv3: 0, judge: 3, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Rejected` }, o => owes(o, {}))
  // J. Adversary 1 returns nothing twice: adversary 2 still runs once, nothing overwrites its log, and no verdict is
  //    written on one log.
  await scenario('J adversary 1 returns nothing twice',
    { scores: two, chosen: ['D1', 'D2'], dead: { [`adversary1:${ID('01')}`]: 2 } },
    { drafts: 4, develop: 2, research: 2, adv1: 3, adv2: 2, adv3: 0, judge: 1, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:null ${ID('02')}:Provisional` },
    o => o.equalisedIds.length ? 'equalisedIds should be empty' : owes(o, { adversaryOwedIds: [ID('01')], noVerdictIds: [ID('01')], rerunUndecided: true }))
  // K. The second adversary of a candidate the first one rejected returns nothing twice: no verdict on one log.
  await scenario('K the Equalise adversary returns nothing twice',
    { scores: two, chosen: ['D1', 'D2'], a1: { '02': 'Rejected' }, judge: { '02': 'Rejected' }, dead: { [`adversary2:${ID('02')}`]: 2 } },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 3, adv3: 0, judge: 1, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:null` },
    o => o.equalisedIds.length ? 'equalisedIds should be empty' : owes(o, { adversaryOwedIds: [ID('02')], noVerdictIds: [ID('02')], rerunUndecided: true }))
  // L. The ranker's chosen list has a stray space, a repeat and a key that is no draft, and leaves out a draft that
  //    scored 2: the two highest-scoring kept drafts are developed all the same, highest first.
  await scenario('L a chosen list that cannot be read as written',
    { scores: { D1: 2, D2: 3, D3: 1, D4: 1 }, chosen: [' d2 ', 'D2', 'X9'] },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 2, adv3: 2, judge: 2, rejudge: 2, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Provisional` },
    o => o.candidates[0].headline === 'H D2' && o.candidates[1].headline === 'H D1' ? owes(o, {}) : 'expected D2 then D1')
  // M. In the rerun one third adversary returns nothing twice: that candidate keeps its first verdict, and its
  //    second judge is not run on a log that does not exist.
  await scenario('M a rerun adversary returns nothing twice',
    { scores: two, chosen: ['D1', 'D2'], dead: { [`adversary3:${ID('01')}`]: 2 } },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 2, adv3: 3, judge: 2, rejudge: 1, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Provisional` },
    o => !same(o.rerunIds, [ID('02')]) ? 'rerunIds should name only the candidate whose rerun finished' : owes(o, { rerunOwed: [ID('01')] }))
  // N. The re-developer returns nothing twice: the re-development is reported as owed.
  await scenario('N the re-developer returns nothing twice',
    { scores: { D1: 1, D2: 2, D3: 1, D4: 1 }, chosen: ['D2'], low: ['01'], judge: { '01': 'Rejected' }, redevelop: ['01'], dead: { [`redevelop:${ID('01')}`]: 2 } },
    { drafts: 4, develop: 1, research: 1, adv1: 1, adv2: 1, adv3: 0, judge: 1, rejudge: 0, redevelop: 2, candidates: `${ID('01')}:Rejected` },
    o => !same(o.redevelopOwed, [ID('01')]) || o.redevelopedIds.length ? 'the failed re-development is not reported as owed' : owes(o, {}))
  // O. The four methods passed as one string: stopped with the same plain message as E, before any agent.
  await scenario('O methods passed as one string', { scores: {}, chosen: [], methods: METHODS.join(', ') }, { error: true },
    (o, p, err, calls) => calls.length ? 'an agent was called' : /args\.methods must be an array/.test(err.message) ? '' : 'stopped for another reason: ' + err.message)
  // P. The researcher finds the candidate outside the five fields: the judge is handed the researcher's own words,
  //    and a Gate 0 rejection is not re-developed even when the judge marks it.
  await scenario('P a field failure reaches the judge',
    { scores: { D1: 2, D2: 1, D3: 1, D4: 1 }, chosen: ['D1'], depthFail: { '01': 'DEPTH FAIL (field): the target field is economics' }, judge: { '01': 'Rejected' }, redevelop: ['01'] },
    { drafts: 4, develop: 1, research: 1, adv1: 0, adv2: 0, adv3: 0, judge: 1, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:Rejected` },
    (o, p) => p[`judge:${ID('01')}`].includes('DEPTH FAIL (field): the target field is economics') ? owes(o, {}) : 'the judge was not handed the researcher\'s summary')
  // Q. An under-asked record that names no raising source: no prompt carries the text "undefined".
  await scenario('Q under-asked with no raising source named',
    { scores: two, chosen: ['D1', 'D2'], underAsked: true },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 2, adv3: 2, judge: 2, rejudge: 2, redevelop: 0, candidates: `${ID('01')}:Provisional ${ID('02')}:Provisional` }, o => owes(o, {}))
  // R. An agent throws (the harness does that when a token budget is exhausted): the candidate stays in the return.
  await scenario('R an adversary throws',
    { scores: two, chosen: ['D1', 'D2'], throws: [`adversary1:${ID('01')}`] },
    { drafts: 4, develop: 2, research: 2, adv1: 2, adv2: 1, adv3: 0, judge: 1, rejudge: 0, redevelop: 0, candidates: `${ID('01')}:null ${ID('02')}:Provisional` },
    o => owes(o, { noVerdictIds: [ID('01')], rerunUndecided: true }))
  console.log(process.exitCode ? 'DRY RUN FAILED' : 'DRY RUN PASSED: 18 scenarios')
})()
