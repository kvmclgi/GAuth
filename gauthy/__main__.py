import binascii
import pathlib
import time
from datetime import datetime, timedelta
from pathlib import Path

import click
import pyotp
import typer
from gen_totp import GenTotp

app = typer.Typer(help="CLI tool to generate google authenticator TOTP.")

auth_key_help = "Provide Authenticator Key for which TOTP needs to be generated"


def get_uri_from_file(auth_file):
    uri_list = []
    file_extension = pathlib.Path(auth_file).suffix
    if file_extension in (".txt", ".yml", ".yaml"):
        try:
            with open(auth_file, "r") as file_object:
                uri_list = file_object.readlines()
                return uri_list
        except FileNotFoundError:
            return uri_list
    else:
        error_message = typer.style(
            f"Supported file formats are - \n1. txt\n2. yml or yaml", fg=typer.colors.BRIGHT_MAGENTA)
        typer.echo(error_message)
        raise typer.Exit(code=1)


def create_totp_list(uri_list: list, totp=None, auth_file=None, add_to_file: bool = False):
    totp_list = []
    if totp:
        totp.now()
        if auth_file and not any(totp.secret == pyotp.parse_uri(key_uri).secret for key_uri in uri_list):
            if add_to_file:
                key_name = typer.prompt(
                    text="Please provide a name/label for the Key",
                    default=totp.name,
                    show_default=True,
                )
                uri_list.append(totp.provisioning_uri(name=key_name))
                try:
                    with open(auth_file, "w") as file_object:
                        file_object.write('\n'.join(uri_list))
                    typer.secho(f"Added Authenticator Key to file", fg=typer.colors.BRIGHT_GREEN)
                except IOError:
                    error_message = typer.style(
                        f"Error adding URI to file", fg=typer.colors.BRIGHT_RED)
                    typer.echo(error_message)
                    raise typer.Exit(code=1)
                finally:
                    file_object.close()
            else:
                uri_list.append(totp.provisioning_uri())
        else:
            if add_to_file:
                typer.secho(f"Authenticator key already exists", fg=typer.colors.BRIGHT_BLUE)
            if not any(totp.secret == pyotp.parse_uri(key_uri).secret for key_uri in uri_list):
                uri_list.append(totp.provisioning_uri())
    for uri in uri_list:
        totp_list.append(pyotp.parse_uri(uri))

    return totp_list


@app.command()
def save(
        auth_file: Path = typer.Argument(
            ...,
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
            metavar="file"),
        auth_key: str = typer.Option(None, "--key", "-k", metavar="Authenticator_Key", help=auth_key_help),
        qr_code: Path = typer.Option(
            None, "--qr", "-q",
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
):
    try:
        totp = None
        uri_list = []
        if auth_file:
            uri_list = get_uri_from_file(auth_file=auth_file)
        if auth_key:
            totp = GenTotp.gen_totp(auth_key)
        elif qr_code:
            totp = GenTotp.decode_qr_code(qr_code)
        totp_list = create_totp_list(totp=totp, auth_file=auth_file, uri_list=uri_list, add_to_file=True)
        display_flag = typer.confirm("Do you want to generate TOTP from file?", default=True, show_default=True)
        if display_flag:
            display_output(totp_list=totp_list, current=False)
        else:
            typer.echo("Goodbye...")

    except KeyboardInterrupt:
        typer.echo("Goodbye...")
        raise typer.Exit(code=0)

    except binascii.Error as err:
        typer.echo("Error - Unable to generate TOTP")
        typer.echo(f"Exception type - binascii.Error \nError message - {err}")
        raise typer.Exit(code=1)


def display_output(totp_list, current):
    validity = 0
    while True:
        click.clear()
        if current:
            typer.echo(f"{'TOTP': >6}{'Name': >25}{'Valid for': >20}")
            for totp in totp_list:
                validity = totp.interval - datetime.now().timestamp() % totp.interval
                typer.echo(f"{totp.now(): >6}{totp.name: >25}{round(validity, 2): >20}s")
            raise typer.Exit()
        typer.echo(f"PREV\t\tCURRENT\t\tNEXT\t\tNAME")
        for totp in totp_list:
            validity = totp.interval - datetime.now().timestamp() % totp.interval
            prev_totp = typer.style(
                f"{totp.at(for_time=datetime.now() - timedelta(seconds=30))}", fg=typer.colors.RED, dim=True)
            curr_totp = typer.style(
                f"{totp.now()}", fg=typer.colors.BRIGHT_GREEN, bold=True)
            next_totp = typer.style(
                f"{totp.at(for_time=datetime.now() + timedelta(seconds=30))}", fg=typer.colors.BLUE, dim=True)
            typer.echo(f"{prev_totp}\t\t{curr_totp}\t\t{next_totp}\t\t{totp.name}")
        with typer.progressbar(
                range(int(validity)), label="Token Validity") as progress:
            for value in progress:
                time.sleep(1)
        time.sleep(0.05)


@app.command()
def generate(auth_key: str = typer.Option(None, "--key", "-k", metavar="Authenticator_Key", help=auth_key_help),
             qr_code: Path = typer.Option(
                 None, "--qr", "-q",
                 exists=True,
                 file_okay=True,
                 dir_okay=False,
                 writable=False,
                 readable=True,
                 resolve_path=True,
             ),
             auth_file: Path = typer.Option(
                 None, "--file", "-f",
                 exists=False,
                 file_okay=True,
                 dir_okay=False,
                 writable=True,
                 readable=True,
                 resolve_path=True,
             ),
             current: bool = typer.Option(False, "--current", "-c")):
    """
    Cli Tool to generate Google Authenticator TOTP

    Usage: python gauthy [--key/-k Authenticator_Key|--qr/-q Path_To_Qr_Image/--file/-f Storage_File] [--current/-c]
    \f
    :param current:
    :param qr_code:
    :param auth_key:
    :param auth_file:
    :return:
    """
    no_of_options = sum(x is not None for x in [auth_key, qr_code, auth_file])

    if (not auth_key and not qr_code and not auth_file) or no_of_options > 1:
        typer.echo(
            "Error: Requires command line option either ['--key' / '-k'] or ['--qr' / '-q'] or ['--file' / '-f']")
        typer.echo("Usage: python gauthy [--key/-k Authenticator_Key | --qr/-q Path_To_Qr_Image | --file/-f "
                   "Storage_File] [--current/-c]")
        raise typer.Exit(code=1)
    try:
        totp = None
        uri_list = []

        if auth_file:
            uri_list = get_uri_from_file(auth_file=auth_file)
        if auth_key:
            totp = GenTotp.gen_totp(auth_key)
        elif qr_code:
            totp = GenTotp.decode_qr_code(qr_code)

        totp_list = create_totp_list(totp=totp, auth_file=auth_file, uri_list=uri_list)

        display_output(totp_list=totp_list, current=current)

    except KeyboardInterrupt:
        typer.echo("Goodbye...")
        raise typer.Exit(code=0)
    except binascii.Error as err:
        typer.echo("Error - Unable to generate TOTP")
        typer.echo(f"Exception type - binascii.Error \nError message - {err}")
        raise typer.Exit(code=1)


if __name__ == '__main__':
    app(prog_name="GAuthy")
