#!/bin/bash
cd "$(dirname "$0")"

#source activate mod-sub && python -c "import save_mod_lists; save_mod_lists.run()"
#source activate mod-sub && python -c "import save_mod_subs; save_mod_subs.run_both()"
source activate mod-sub && python -c "import run_script; run_script.run_both()"
