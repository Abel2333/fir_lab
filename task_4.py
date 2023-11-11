import numpy as np
from util.fir_filter import FIRFilter
import matplotlib.pylab as plt


def draw_figures(sample, template, ecg_signal, real_peaks, heart_rate, heart_time, path):
    """
    Draw some figures to illustrate the process and result of detect 
    R-peaks in pre-processing ecg signal
    """
    plt.figure(figsize=(14, 9))

    plt.subplot(3, 1, 1)
    plt.plot(np.arange(len(template)) / sample, template)
    plt.title("ECG Template")
    plt.xlabel("Time(s)")
    plt.ylabel("Amplitude")
    
    total_time = np.arange(len(ecg_signal)) / sample
    plt.subplot(3, 1, 2)
    plt.plot(total_time, ecg_signal, label="Orignal ECG Signal")
    plt.plot(real_peaks / sample, ecg_signal[real_peaks], "ro", label="R-peaks")
    plt.title("R-peaks Detection")
    plt.xlabel("Time(s)")
    plt.ylabel("Amplitude")
    plt.legend(loc="best", frameon=False, prop=None, fontsize=7)
    
    plt.subplot(3, 1, 3)
    plt.plot(heart_time, heart_rate)
    plt.title("Heartrate Against Time")
    plt.xlabel("Time(s)")
    plt.ylabel("Heart rate")
    
    plt.tight_layout()
    plt.show()
    plt.savefig(path)


def detect_R_peaks(ecg_signal, sample, template, save_path):
    """
    Detect R-peaks from pre-processing ECG signal,
    which basially need to remove baseline and 50Hz noise.
    Then draw some figures to show the result and process

    Parameters:
        ecg_signal: ECG signal after pre-processing
        sample: Sample rate of the signal
        template: Template signal to match each QRS period
        save_path: The path to save figure
    
    Returns:
        No return

    Raises:
        ValueError: when template is longer than sample
    """

    if len(template) > len(ecg_signal):
        raise ValueError("ECG signal should longer than template wave")
    
    # Generate a matched filter
    fir_coeff = template[::-1]  # for convolution, this template should be inversed
    matched_filter = FIRFilter(fir_coeff)

    # Perpare for detect R-peaks
    detect_signal = np.zeros(
        len(ecg_signal) + matched_filter.coefficients_length - 1
    )  # Singal after convolution
    threshould = 20  # Threshould for detect_signal
    highest_point = 0  # Position of local highest
    new_peak = False  # Indicate if we get new real_peak based on approx_point
    pass_point = list()  # Higher than threshould in detect_signal
    real_peaks = list()  # Real peaks
    approx_peaks = list()  # Approximately peaks acquired from detect_signal
    heart_rate = list()  # Record the heart rate
    heart_time = list()  # Record the real time for each heart rate

    # Detect the R-peaks against time
    # approximately peaks must be in the vicinity of real peaks
    # Length of convolution is m+n-1, and padding 0
    for i in range(0, len(ecg_signal) + matched_filter.coefficients_length - 1):
        if i < len(ecg_signal):
            # Convolution, square, and record the local highest point
            if ecg_signal[highest_point] < ecg_signal[i]:
                highest_point = i
            detect_signal[i] = matched_filter.dofilter(ecg_signal[i]) ** 2
        else:
            detect_signal[i] = matched_filter.dofilter(0) ** 2
        # Impose the threshould
        if detect_signal[i] < threshould:
            detect_signal[i] = 0
        else:
            pass_point.append(i)

        # approx_peaks must be the peak of pass_point
        if (
            len(pass_point) >= 3
            and detect_signal[pass_point[-2]] > detect_signal[pass_point[-3]]
            and detect_signal[pass_point[-2]] > detect_signal[pass_point[-1]]
        ):
            # Only use one point in per QRS period in detect_signal
            if len(approx_peaks) == 0 or (
                len(approx_peaks) > 0
                and pass_point[-2] - approx_peaks[-1] > (0.05 * sample)
            ):
                approx_peaks.append(
                    int(pass_point[-2] - (matched_filter.coefficients_length - 1) / 2)
                )
                # new_peak means real_peak can acquire a peak
                new_peak = True

        # The main idea is this:
        # we can understand where the highest points are only if
        # we past that point long enough (0.05 seconds in this code).
        # And the distance between highest point and corresponding approximately peak
        # never long than 0.3 seconds (QRS period normally less than 0.5 seconds).
        if (
            new_peak
            and len(approx_peaks) > 0
            and np.abs(i - approx_peaks[-1]) < (0.3 * sample)
            and i - highest_point > (0.05 * sample)
        ):
            real_peaks.append(highest_point)
            highest_point = 0
            new_peak = False
            # Caculating heart rate
            if len(real_peaks) > 1:
                heart_rate.append(60 / ((real_peaks[-1] - real_peaks[-2]) / sample))
                heart_time.append(real_peaks[-1] / sample)

    real_peaks = np.array(real_peaks)
    draw_figures(sample, template, ecg_signal, real_peaks, heart_rate, heart_time, path=save_path)


def main():
    ecg = np.loadtxt("data/new_ECG.dat")
    template = np.loadtxt("data/ECG_template_1000Hz.dat")
    detect_R_peaks(ecg, sample=1000, template=template, save_path="figures/detect_R_peaks.jpeg")


if __name__ == "__main__":
    main()
