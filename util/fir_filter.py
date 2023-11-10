import numpy as np

class FIRDesign:
    def __init__(self, _sample) -> None:
        self.sample = _sample
    
    def highpass_design(self, high_frequency, frequency_resulotion) -> np.array:
        M = int(self.sample / frequency_resulotion)

        # Generate the ideal filter, from frequency domain to time domain
        ideal_filter = np.zeros(M)
        highband = int(high_frequency/self.sample * M)
        ideal_filter[highband:M-highband+1] = 1
        ideal_filter = np.fft.ifft(ideal_filter).real
        
        # Generate actually filter coefficients
        filter_coefficients = np.empty(M)
        filter_coefficients[0:int(M/2)] = ideal_filter[int(M/2):M]
        filter_coefficients[int(M/2):M] = ideal_filter[0:int(M/2)]
        filter_coefficients = filter_coefficients * np.hamming(M)
        return filter_coefficients
    
    def bandstopDesign(self, low_frequency, high_frequency, frequency_resulotion) -> np.array:
        M = int(self.sample / frequency_resulotion)
        
        # Generate the ideal filter, from frequency domain to time domain
        ideal_filter = np.ones(M)
        low_band = int(low_frequency/self.sample * M)
        high_band = int(high_frequency/self.sample * M)
        ideal_filter[low_band:high_band+1] = 0
        ideal_filter[M-high_band:M-low_band+1] = 0
        ideal_filter = np.fft.ifft(ideal_filter).real

        # Generate actually filter coefficients
        filter_coefficients = np.empty(M)
        filter_coefficients[0:int(M/2)] = ideal_filter[int(M/2):M]
        filter_coefficients[int(M/2):M] = ideal_filter[0:int(M/2)]
        filter_coefficients = filter_coefficients * np.hamming(M)
        return filter_coefficients
    

class FIRFilter:
    def __init__(self, _coefficients:list):
        # List can contain many lists with different length
        self.coefficients_list = [_coefficients]
        self.real_coefficients = _coefficients
        self.coefficients_length = len(self.real_coefficients)
        self.buffer = np.zeros(self.coefficients_length)

    def add_coefficients(self, _coefficients:list):
        self.coefficients_list.append(_coefficients)

    def synthesis(self):
        # Get real coefficients from list
        if len(self.coefficients_list) == 1:
            return
        tmp = self.coefficients_list[0]
        for coeff in self.coefficients_list[1::]:
            tmp = self.convolution(coeff, tmp)
        self.real_coefficients = tmp
        self.coefficients_length = len(self.real_coefficients)
        self.buffer = np.zeros(self.coefficients_length)


    def convolution(self, x_1:list, x_2:list):
        n = len(x_1)
        m = len(x_2)
        x_1 = np.array(x_1)
        x_2 = np.array(x_2)
        tmp = np.zeros(2*n+m)
        tmp[n-1:n+m-1] = x_2
        result = np.empty(m+n-1)
        for i in range(0, m+n-1):
            result[i] = np.dot(x_1, tmp[i:i+n][::-1])
        return result


    def dofilter(self, v):
        # Shift values in the buffer
        self.buffer[1:] = self.buffer[:-1]
        self.buffer[0] = v

        # Apply the filter
        result = np.dot(self.real_coefficients, self.buffer)

        return result
    