"""Static LLVM SSA/effect contracts, never an ISA or MMIO executor."""
import re

WRITE = 'tsl9_nv_write_callback_197be'
TIMER = 'tsl9_delay_19764'
HELPERS = ['tsl9_flash_' + n for n in ('status_18e90', 'unlock_18e98', 'lock_18eb6', 'erase_18ec4', 'program_18ef2', 'quarter_9c0a')]


def need(value, why):
    if not value:
        raise ValueError(why)


def bodies(text):
    return {m[1]: (m[2], m[3]) for m in re.finditer(r'^define[^\n]*?@([A-Za-z0-9_]+)\(([^\n]*)\)[^\n]*\{\n(.*?)^}', text, re.M | re.S)}


def contract(text):
    functions = bodies(text)
    need(set(functions) == set(HELPERS + [WRITE, TIMER]), 'Eight actual LLVM definitions, no invented provider')
    params, body = functions[WRITE]
    need(params == 'i32 noundef %0, i32 noundef %1, i32 noundef %2', 'Write genuine three-u32 call surface')
    lines = [x.strip() for x in body.splitlines() if x.strip()]
    patterns = [
        r'%4 = tail call (?:noundef )?i32 @tsl9_flash_unlock_18e98\(i32 noundef %0\) #\d+',
        r'%5 = tail call (?:noundef )?i32 @tsl9_flash_erase_18ec4\(i32 noundef %0\) #\d+',
        r'%6 = tail call (?:noundef )?i32 @tsl9_flash_program_18ef2\(i32 noundef %0, i32 noundef %2\) #\d+',
        r'%7 = tail call (?:noundef )?i32 @tsl9_flash_lock_18eb6\(i32 noundef %6\) #\d+',
        r'%8 = tail call (?:noundef )?i32 @tsl9_delay_19764\(i32 noundef 1\) #\d+',
        r'ret i32 0',
    ]
    need(len(lines) == len(patterns) and all(re.fullmatch(p, x) for p, x in zip(patterns, lines)),
         'Exact five genuine typed calls, origins, program-A0-to-lock and return zero')
    params, body = functions[TIMER]
    need(params == 'i32 noundef returned %0' or params == 'i32 noundef %0', 'Timer genuine one-u32 surface')
    values = {'%0': ('param', 0)}
    effects = []
    gp = []
    branches = []

    def value(token):
        return values[token] if token.startswith('%') else int(token) & 0xffffffff

    for line in body.splitlines():
        line = line.strip()
        m = re.match(r'(%\d+) = (?:tail )?call (?:noundef )?i32 asm sideeffect "mv \$0, gp", "=r,~\{memory\}"\(\) #\d+', line)
        if m:
            values[m[1]] = ('GP',)
            gp.append(len(effects))
            continue
        m = re.match(r'(%\d+) = (and|or|add|mul)(?: nuw)?(?: nsw)? i32 (%\d+|-?\d+), (%\d+|-?\d+)$', line)
        if m:
            values[m[1]] = (m[2], value(m[3]), value(m[4]))
            continue
        m = re.match(r'(%\d+) = inttoptr i32 (%\d+) to ptr$', line)
        if m:
            values[m[1]] = value(m[2])
            continue
        m = re.match(r'(%\d+) = load volatile i(8|32), ptr (?:inttoptr \(i32 (-?\d+) to ptr\)|(%\d+)),', line)
        if m:
            address = int(m[3]) & 0xffffffff if m[3] else value(m[4])
            effects.append(('read', int(m[2]), address))
            values[m[1]] = ('read', len(effects) - 1, int(m[2]))
            continue
        m = re.match(r'store volatile i32 (%\d+|-?\d+), ptr inttoptr \(i32 (-?\d+) to ptr\),', line)
        if m:
            effects.append(('write', 32, int(m[2]) & 0xffffffff, value(m[1])))
            continue
        m = re.match(r'(%\d+) = zext i8 (%\d+) to i32$', line)
        if m:
            values[m[1]] = value(m[2])
            continue
        m = re.match(r'(%\d+) = icmp eq i32 (%\d+), 0$', line)
        if m:
            values[m[1]] = ('eq', value(m[2]), 0)
            continue
        m = re.match(r'br i1 (%\d+), label %([\d]+), label %([\d]+)', line)
        if m:
            branches.append((value(m[1]), m[2], m[3]))
            continue
        need(not re.search(r'\b(load|store|call|alloca|asm|icmp)\b', line), 'No hidden timer memory or call effect: ' + line)
    R = lambda i, width=32: ('read', i, width)
    expected = [('read', 32, 0xe000f004), ('write', 32, 0xe000f004, ('and', R(0), 0xfffffffe)),
                ('read', 8, ('add', ('GP',), 382)),
                ('write', 32, 0xe000f010, ('mul', R(2, 8), ('param', 0))),
                ('write', 32, 0xe000f014, 0),
                ('read', 32, 0xe000f000), ('write', 32, 0xe000f000, ('or', R(5), 16)),
                ('read', 32, 0xe000f000), ('write', 32, 0xe000f000, ('or', R(7), 33)),
                ('read', 32, 0xe000f004),
                ('read', 32, 0xe000f000), ('write', 32, 0xe000f000, ('and', R(10), 0xfffffffe))]
    need(effects == expected and gp == [2], 'Every fresh timer volatile effect/data origin/order, live GP after initial store')
    need(len(branches) == 1 and branches[0][0] == ('eq', ('and', R(9), 1), 0), 'Timer loops while fresh bit0 is clear')
    poll = re.search(r'^(\d+):[^\n]*\n\s*(%\d+) = load volatile i32, ptr inttoptr \(i32 -536809468 to ptr\)', body, re.M)
    need(poll is not None and branches[0][1] == poll[1], 'Timer true branch targets actual fresh status read block')
    need(re.findall(r'^\s*ret i32 ([^\n]+)', body, re.M) == ['%0'], 'Timer normal A0 returns original input')
    return dict(definitions=8, write_calls=5, write_unused_parameter=1, timer_minimum_volatile_effects=12,
                fresh_GP_read=True, timer_returns_input=True, timer_unbounded_poll_until_bit0_set=True,
                program_A0_result_passed_to_lock=True, physical_prototypes_recovered=False,
                normal_effect_projection_only=True)
