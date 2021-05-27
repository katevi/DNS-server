Homework for telecom course at St. Petersburg State University.

**Simple DNS-server with blacklist**

Provides the user with the ability to specify in `settings.json` file next settings:
- DNS-server to redirect requests
- domain names for which getting ip will be prohibited
- server IP

You can test it with standard utility `nslookup` in Windows, or `dig` in Unix-based systems. Taking `127.0.0.1` as server address from `settings.json`, following examples present interaction with DNS-server via utilits, written above:
 - `nslookup vk.com 127.0.0.1`
 - `dig vk.com @127.0.0.1`

Feel free to contribute!
