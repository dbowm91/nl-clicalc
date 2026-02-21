# Fish completion for clicalc

# Disable file completion by default
complete -c clicalc -f

# Options
complete -c clicalc -s h -l help -d 'Show help message'
complete -c clicalc -s v -l version -d 'Show version information'
complete -c clicalc -s e -l expression -d 'Evaluate a single expression' -x
complete -c clicalc -s q -l quiet -d 'Suppress expression in output'
complete -c clicalc -s s -l show -d 'Show expression in output'
complete -c clicalc -l json -d 'Output result as JSON'
complete -c clicalc -s i -l interactive -d 'Start interactive REPL mode'

# Functions
complete -c clicalc -n '__fish_use_subcommand' -a 'sin cos tan asin acos atan sinh cosh tanh' -d 'Trigonometric function'
complete -c clicalc -n '__fish_use_subcommand' -a 'sqrt log log10 log2 exp' -d 'Mathematical function'
complete -c clicalc -n '__fish_use_subcommand' -a 'abs floor ceil round' -d 'Rounding function'
complete -c clicalc -n '__fish_use_subcommand' -a 'factorial gcd lcm perm comb nPr nCr' -d 'Combinatorics function'
complete -c clicalc -n '__fish_use_subcommand' -a 'mean median mode std variance sum min max' -d 'Statistics function'
complete -c clicalc -n '__fish_use_subcommand' -a 'isprime primefactors nextprime prevprime' -d 'Prime function'

# Constants
complete -c clicalc -n '__fish_use_subcommand' -a 'pi' -d 'Mathematical constant π'
complete -c clicalc -n '__fish_use_subcommand' -a 'e' -d 'Euler\'s number'
complete -c clicalc -n '__fish_use_subcommand' -a 'tau' -d '2π'
complete -c clicalc -n '__fish_use_subcommand' -a 'i' -d 'Imaginary unit'
complete -c clicalc -n '__fish_use_subcommand' -a 'avogadro' -d 'Avogadro constant'
complete -c clicalc -n '__fish_use_subcommand' -a 'planck' -d 'Planck constant'
complete -c clicalc -n '__fish_use_subcommand' -a 'boltzmann' -d 'Boltzmann constant'
complete -c clicalc -n '__fish_use_subcommand' -a 'c' -d 'Speed of light'

# Units
complete -c clicalc -n '__fish_use_subcommand' -a 'm km cm mm in ft yd mi' -d 'Length unit'
complete -c clicalc -n '__fish_use_subcommand' -a 's ms min h d wk yr' -d 'Time unit'
complete -c clicalc -n '__fish_use_subcommand' -a 'B KB MB GB TB' -d 'Data unit'
complete -c clicalc -n '__fish_use_subcommand' -a 'kg g mg lb oz' -d 'Mass unit'
complete -c clicalc -n '__fish_use_subcommand' -a 'L mL gal' -d 'Volume unit'
