#!/bin/bash
cd "$(dirname "$0")"

source activate mod-sub && python -c "import save_mod_subs; save_mod_subs.run_both()"
