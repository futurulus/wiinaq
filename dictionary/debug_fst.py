import argparse

from . import alutiiq_fst as af
from . import alutiiq as a


def debug():
    from tqdm import tqdm

    parser = argparse.ArgumentParser()
    parser.add_argument('--root', '-r')
    parser.add_argument('--pos', '-p')
    parser.add_argument('--features', '-f')
    parser.add_argument('--slow', '-s', action='store_true', help='Build the full FST instead of projecting onto the query')
    parser.add_argument('--query', '-q', help='Raw query (instead of root/pos/features)')
    options = parser.parse_args()

    lines = af.COMBINATION_RULES.splitlines()
    if options.query:
        query = options.query
    else:
        endings_map = a.get_endings_map(options.pos)
        query = f"{af.escape(options.root)} {af.escape(endings_map[options.features])}"

    result = [query]
    print(f"  {query}")

    if options.slow:
        fst = None
    else:
        fst = query

    with tqdm(lines) as progress:
        for line in progress:
            if line.strip() != "*" and ('/' not in line or line.strip().startswith('#')):
                continue

            if fst and line.strip() == "*":
                fst.optimize()
            else:
                try:
                    rule_fst = af.parse_rule(line)
                    if fst is None:
                        fst = rule_fst
                    else:
                        fst @= rule_fst
                except Exception:
                    progress.write(line.strip())
                    raise

            new_result = process(fst, query)
            if new_result != result:
                progress.write(line.strip())
                for form in new_result:
                    progress.write(f"  {form}")
                result = new_result


def process(fst, query):
    result_fst = query @ fst
    result_fst.set_input_symbols(af.global_symbol_table())
    result_fst.set_output_symbols(af.global_symbol_table())
    return sorted(af.paths_acc(result_fst))


if __name__ == "__main__":
    debug()