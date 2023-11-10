from util.fir_filter import FIRDesign, FIRFilter
import numpy as np
import matplotlib.pyplot as plt


def main():
    ecg_signal = np.loadtxt("data/ECG_1000Hz_7.dat")
    filter_design = FIRDesign(1000)
    coeff_highpass = filter_design.highpass_design(
        high_frequency=1, frequency_resulotion=0.5
    )
    coeff_bandstop = filter_design.bandstopDesign(
        low_frequency=49, high_frequency=51, frequency_resulotion=0.5
    )

    filter = FIRFilter(coeff_highpass)
    filter.add_coefficients(coeff_bandstop)
    filter.synthesis()

    new_signal = np.zeros(len(ecg_signal)+filter.coefficients_length-1)

    for i in range(0, len(ecg_signal)+filter.coefficients_length-1):
        if i < len(ecg_signal):
            new_signal[i] = filter.dofilter(ecg_signal[i])
        else:
            new_signal[i] = filter.dofilter(0)

    time = np.arange(0, len(new_signal)) / 1000
    plt.plot(time, new_signal)
    plt.savefig("./figures.jpeg")


if __name__ == "__main__":
    main()
