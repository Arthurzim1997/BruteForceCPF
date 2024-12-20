import argparse
import re


class ArgsValidator:
    def _validate_yes_or_no_argument(self, arg: str) -> str:
        valids = ("yes", "no")

        if arg not in valids:
            raise argparse.ArgumentError(f"The argument {arg} is invalid ...")

        return arg

    def validate_cpf(self, cpf: str) -> str:
        pattern = r"^[\dX]{3}\.[\dX]{3}\.[\dX]{3}-[\dX]{2}$"

        if not re.match(pattern, cpf):
            raise argparse.ArgumentError(f"The CPF argument is invalid ...")
        
        return cpf

    def validate_file(self, file: str) -> str:
        return self._validate_yes_or_no_argument(file)