from model import Participants

db = Participants("predictions.db")
percentage = (0.8, 0.2)
coefficients = ()


class Coefficients:

    @staticmethod
    def get_coefficients():
        Coefficients.calc_coefs()
        return coefficients

    @staticmethod
    def calc_coefs():
        global coefficients
        pass_sum = db.get_pred_by_type("pass")[1]
        fail_sum = db.get_pred_by_type("fail")[1]

        if not pass_sum and not fail_sum:
            coefficients = (1 / percentage[0], 1 / percentage[1])
        else:
            pass_sum, fail_sum = int(pass_sum), int(fail_sum)

        Coefficients.balance_percentage(fail_sum, pass_sum)

    @staticmethod
    def balance_percentage(fail_sum, pass_sum):
        summary = pass_sum + fail_sum

        pass_perc, fail_perc = Coefficients.is_zero_chance(pass_sum / summary, fail_sum / summary)

        pass_delta, fail_delta = Coefficients.get_deltas(pass_perc, fail_perc)
        pass_perc += pass_delta
        fail_perc += fail_delta

        Coefficients.set_coefs(pass_perc, fail_perc)

    @staticmethod
    def is_zero_chance(pass_perc, fail_perc):
        if fail_perc == 0:
            fail_perc = 0.01
        elif pass_perc == 0:
            pass_perc = 0.01
        return pass_perc, fail_perc

    @staticmethod
    def get_deltas(pass_perc, fail_perc):
        pass_delta = pass_perc - percentage[0]
        fail_delta = fail_perc - percentage[1]
        return pass_delta, fail_delta

    @staticmethod
    def set_coefs(pass_perc, fail_perc):
        global coefficients
        p_coef = round(1 / pass_perc, 2)
        f_coef = round(1 / fail_perc, 2)
        coefficients = (p_coef, f_coef)
