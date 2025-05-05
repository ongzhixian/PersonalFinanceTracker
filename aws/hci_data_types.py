class SGID(object):
    """
    SGID is a 9 character long string
    # 123456789
    # @1234567C
    # Letter "S", "T", "F", "G" or "M"
    # 7-digit
    # Checksum
    """
    def __init__(self, raw_string):
        self.raw_data = raw_string

    def has_valid_status_char(self):
        valid_status_character_list = [
             'S' # Singapore citizens and permanent residents born before 1 January 2000
            ,'T' # Singapore citizens and permanent residents born on or after 1 January 2000
            ,'F' # Foreigners issued with long-term passes before 1 January 2000
            ,'G' # Foreigners issued with long-term passes from 1 January 2000 to 31 December 2021
            ,'M' # Foreigners issued with long-term passes on or after 1 January 2022
        ]
        return self.raw_data[0] in valid_status_character_list

    def has_valid_checksum_char(self):
        """
        The steps involved in the computation are as follows:

        Multiply each digit in the NRIC number by its weight i.e. 2 7 6 5 4 3 2 in order.
        Add together the above products.
        If the first letter i.e. UIN of the NRIC starts with T or G, add 4 to the total.
        Find the remainder of (sum calculated above) mod 11.
        If the NRIC starts with F or G: 0=X, 1=W, 2=U, 3=T, 4=R, 5=Q, 6=P, 7=N, 8=M, 9=L, 10=K
        If the NRIC starts with S or T: 0=J, 1=Z, 2=I, 3=H, 4=G, 5=F, 6=E, 7=D, 8=C, 9=B, 10=A
        """
        #          1  2  3  4  5  6  7
        weights = [2, 7, 6, 5, 4, 3, 2]
        #               0    1    2    3    4    5    6    7    8    9   10
        sgp_map     = ['J', 'Z', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
        non_sgp_map = ['X', 'W', 'U', 'T', 'R', 'Q', 'P', 'N', 'M', 'L', 'K']
        post_2000_char_list = ['T', 'G']

        issue_char = self.raw_data[0]
        sum_of_checks = 0

        for index, number in enumerate(list(self.raw_data[1:8])): sum_of_checks = sum_of_checks + (weights[index] * int(number))

        if issue_char in post_2000_char_list:
            sum_of_checks = sum_of_checks + 4

        checksum_modulus = sum_of_checks % 11

        sgp_char_list = ['S', 'T']

        return self.raw_data[8] == sgp_map[checksum_modulus] if issue_char in sgp_char_list else non_sgp_map[checksum_modulus]

    def is_valid(self):
        if len(self.raw_data) != 9:
            return False
        if not self.has_valid_status_char():
            return False
        if not self.has_valid_checksum_char():
            return False


if __name__ == '__main__':
    sgid = SGID('xxx')
    is_valid = sgid.has_valid_checksum_char()
    print('is_valid', is_valid)