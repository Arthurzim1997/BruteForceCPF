import argparse
import itertools
import textwrap
import threading

from args_validator import ArgsValidator

DIGITS = "0123456789"

CPF_LENGTH_WITHOUT_PONCTUATION = 11
CPF_LENGTH_WITH_PONCTUATION = 14


def print_line():
    print("-" * 40)


class BFCPF:
    def __init__(self, args) -> None:
        self.args = args
        self.output = ""

        self.sanitized_cpf = self.sanitize_cpf(self.args.cpf)

        # Lista para armazenar os CPFs válidos encontrados
        self.valid_cpfs = []

    def save_output_to_file(self) -> None:
        output_file_path = f"{self.args.cpf}.txt"

        with open(output_file_path, "w") as output_file:
            output_file.write(self.output)

    def print_output(self) -> None:
        print(self.output)

    def main_menu(self):
        with open("./interface/main_menu.txt", "r") as main_menu_file:
            print(main_menu_file.read())

    def is_character_valid(self, character: str) -> str:
        if character in DIGITS:
            return character

        if character == "X":
            return character

        return ""

    def sanitize_cpf(self, cpf: str) -> str:
        assert len(cpf) == CPF_LENGTH_WITH_PONCTUATION

        return "".join(filter(self.is_character_valid, cpf))

    def desanitize_cpf(self, cpf: str) -> str:
        assert len(cpf) == CPF_LENGTH_WITHOUT_PONCTUATION

        desanitized_cpf = f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

        return desanitized_cpf

    def calculate_verification_digit(self, partial_cpf: str):
        weights = range(2, 10 + 1)[::-1]

        sum_ = sum(int(partial_cpf[i]) * weights[i] for i in range(len(weights)))
        resto = sum_ % 11

        if resto == 0 or resto == 1:
            return "0"

        return str(11 - resto)

    def is_cpf_valid(self, cpf: str) -> bool:
        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        digito1 = self.calculate_verification_digit(cpf[:9])

        if digito1 != cpf[9]:
            return False

        digito2 = self.calculate_verification_digit(cpf[1:10])

        if digito2 != cpf[10]:
            return False

        return True

    def find_missing_digits_indexes(self, partial_cpf: str) -> list[int]:
        missing_digits_indexes = []

        for i, character in enumerate(partial_cpf):
            if character == "X":
                missing_digits_indexes.append(i)

        return missing_digits_indexes

    def discover_possibilities(self) -> itertools.product:
        missing_digits_indexes = self.find_missing_digits_indexes(self.sanitized_cpf)
        total_missing_digits = len(missing_digits_indexes)

        possibilities = itertools.product(DIGITS, repeat=total_missing_digits)

        return possibilities

    def discover_valid_cpfs_for_possibility(self, possibility: tuple, missing_digits_indexes: list[int]) -> None:
        sanitized_cpf_list = list(self.sanitized_cpf)

        for i, missing_digit_index in enumerate(missing_digits_indexes):
            sanitized_cpf_list[missing_digit_index] = possibility[i]

        cpf = "".join(sanitized_cpf_list)

        # Feedback visual de CPF sendo testado
        print(f"Testing CPF: {cpf}")  # Aqui imprime a combinação sendo testada

        if self.is_cpf_valid(cpf):
            cpf = self.desanitize_cpf(cpf)

            # Usamos o lock para proteger o acesso à lista de resultados
            with threading.Lock():
                self.valid_cpfs.append(cpf)

            # Feedback visual de CPF válido encontrado
            print(f"Valid CPF found: {cpf}")  # Aqui imprime o CPF válido

    def brute_force(self) -> None:
        valid_cpfs = []
        missing_digits_indexes = self.find_missing_digits_indexes(self.sanitized_cpf)
        possibilities = self.discover_possibilities()

        # Criando threads para processar as possibilidades
        threads = []

        # Lançar 25 threads para processar as possibilidades
        for possibility in possibilities:
            thread = threading.Thread(target=self.discover_valid_cpfs_for_possibility, args=(possibility, missing_digits_indexes))
            threads.append(thread)
            thread.start()

            # Controlar o número de threads simultâneas (limitar a 25)
            if len(threads) >= 100:
                for t in threads:
                    t.join()
                threads = []

        # Aguardar todas as threads finalizarem
        for t in threads:
            t.join()

        # Feedback visual de quantos CPFs válidos foram encontrados
        print(f"Total valid CPFs found: {len(self.valid_cpfs)}")  # Exibe o total de CPFs válidos encontrados

        self.output += "Valid CPFs found:\n\n"
        self.output += "\n".join(self.valid_cpfs)

    def run(self):
        self.main_menu()
        print_line()

        self.brute_force()

        if self.args.file == "yes":
            self.save_output_to_file()

        else:
            self.print_output()


def main():
    epilog = ""

    with open("./interface/epilog.txt", "r") as epilog_file:
        epilog = epilog_file.read()

    parser = argparse.ArgumentParser(
        description="CPF Brute Forcer by Gustavo Naldoni & André Zappa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(epilog),
    )

    args_validator = ArgsValidator()

    parser.add_argument(
        "-c",
        "--cpf",
        required=True,
        type=args_validator.validate_cpf,
        help="partial CPF to attack",
    )
    parser.add_argument(
        "-f",
        "--file",
        required=False,
        default="no",
        type=args_validator.validate_file,
        help="output as a file (yes/no)",
    )

    args = parser.parse_args()

    bfcpf = BFCPF(args)
    bfcpf.run()


if __name__ == "__main__":
    main()
