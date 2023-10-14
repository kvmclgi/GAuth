# GAuthy

Cli based Google Authenticator TOTP Generator

## Prerequisites

1. Requires **Python 3.6+**
2. Install requirements using poetry
```commandline
poetry install
```
3.Install **zbar** package
```commandline
pip install zbar
```
For mac user
```commandline
brew install zbar
```
# How to ?

---
### Usage:
```commandline
python gauthy generate [--key/-k Authenticator_Key | --qr/-q Path_To_Qr_Image | --file/-f Storage_File] [--current/-c]
```
## Generate TOTP using Key or QR code:

---
### To generate TOTP using Authenticator Key
```commandline
python gauthy generate -k YOURAUTHKEYHERE
python gauthy generate --key YOURAUTHKEYHERE
```
### To generate TOTP using Authenticator QR code Image
```commandline
python gauthy generate -q path/to/image
python gauthy generate --qr path/to/image
```

## Save and Generate TOTP using file

---
### Usage:
```commandline
# To save to a file
python gauthy save path/to/file [--key/-k Authenticator_Key|--qr/-q Path_To_Qr_Image]

# To generate from a file
python gauthy generate [--file/-f Storage_File] [--current/-c]
```
### To add TOTPs to file
```commandline
# To add Auth key to file
python gauthy save path/to/file -k YOURAUTHKEYHERE

# To add URI from QR image to file
python gauthy save path/to/file -q path/to/image
```

### To generate TOTP using file
```commandline
python gauthy generate -f path/to/file
python gauthy generate --file path/to/file
```
### Other options
1. To display just current TOTP
- Use **_-c / --curent_** flag to display just current TOTP
- Example: 
```commandline
python gauthy -q path/to/image --current
python gauthy --key YOURAUTHKEYHERE -c
```
---
### For help
```commandline
 python gauthy --help
```
