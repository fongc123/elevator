# elevator
Files for elevator floor and door access.

Functions:
- `radd`: allows access to specified floors for a card number
- `radd1`: allows access to specified doors for a card number
- `rdelay`: adds a delay (in seconds) to door open status
- `rdatetime`: returns the date and time of the system
- `status`: get the status of the system

Usage:
- `radd`: `eaccess.exe -radd ip_address port card_number allow floors(csv) board_serial start_date end_date path`
- `radd1`: `eaccess.exe -radd1 ip_address port card_number gates_allow(csv) board_serial start_date end_date`
- `rdelay`: `eaccess.exe -rdelay ip_adress port board_serial door control delay`
- `rdatetime`: `eaccess.exe -rdatetime ip_address port board_serial path`
- `status`: `eaccess.exe -getdata ip_address port board_serial path`
