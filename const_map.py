import numpy as np

from cm_helper import compute_fft

# Provided functions for finding if two peaks are "duplicates" (too close to each other)
def peaks_are_duplicate(peak1: tuple[int, float] = None, peak2: tuple[int,float] = None):
    if peak1 is None or peak2 is None:
        return False
    
    # Threshholds for considering two peaks as duplicates. Feel free to play around with these for your app.
    delta_time = 10
    delta_freq = 300
    t1, f1 = peak1
    t2, f2 = peak2
    if abs(t1 - t2) <= delta_time and abs(f1 - f2) <= delta_freq:
        return True
    return False

# Function to remove duplicate peaks that are too close to each other
def remove_duplicate_peaks(peaks: list[tuple[int, float]]):
    # create a copy of the peaks list to avoid modifying the original list
    peaksc=peaks.copy()
    
    # DONE! TODO: sort peaks by time
    peaksc.sort(key=lambda x: x[0]) 
    
    # DONE! TODO: for each peak, search for duplicates within the next 15 peaks (ordered by time)
    i = 0
    while i < len(peaksc):
        j = i + 1
        while j < min(i + 16, len(peaksc)):
            if peaks_are_duplicate(peaksc[i], peaksc[j]):
                peaksc.pop(j)
            else:
                j += 1
        i += 1

    return peaksc


def find_peaks(frequencies, times, magnitude,
                             window_size=10,
                             candidates_per_band=6):

    return find_peaks_windowed(frequencies, times, magnitude, window_size, candidates_per_band)

def find_peaks_windowed(frequencies, times, magnitude,
                             window_size=10,
                             candidates_per_band=6):
    """
    find the peaks in the spectrum using a sliding window

    within each window spanning the entire frequency range, find the local maxima within sub tiles of the window, then select `peaks_per_window` peaks across all local maxima

    this helps avoid peaks from being clustered too close together

    use `sub_tile_height=None` to just extract top `peaks_per_window` peaks per window across the audio
    """
    constellation_map = []
        
    # Attempt 3: sliding window across time, extract top peaks from each window after
    #            computing local maxima within frequency bands
    num_freq_bins, num_time_bins = magnitude.shape
    constellation_map = []

    
    # TODO: create frequency bands based on logarithmic scale. Assume fft_window_size = 1024
    # Hint: start from 0-40Hz
    bands = [
        (np.searchsorted(freq_bin_hz, edges[i], 'left'), np.searchsorted(freq_bin_hz, edges[i+1], 'right'))
        for i in range(n_bands)
    ]

    # slide a window across time axis
    # height: entire frequency range
    # width:  window_size
    for t_start in range(0, num_time_bins, window_size):
        
        # TODO: Get the window of frequencies we want to work with
        window = magnitude[:, t_start:t_end]

        peak_candidates = []


        # TODO: Find local maxima within the frequency bands of each window
        for f_start, f_end in bands:
            # TODO: Get the frequency band for this window
            freq_square = window[f_start:f_end, :]

            # TODO: Find the indices of the top `candidates_per_band` peaks in the freq_square
            # Hint: Flatten the 2D freq_square to 1D using np.argpartition
            flat = freq_square.flatten()
            if flat.size == 0:
                continue
            N = min(candidates_per_band, flat.size)
            flat_indices = np.argpartition(flat, -N)[-N:]

            # 
            for idx in flat_indices:
                # TODO: calculate the original time and frequency indices from the flattened candidate indices
                # Hint: use np.unravel_index and .shape of freq_square to go from 1D index to 2D index
                rel_f_idx, rel_t_idx = np.unravel_index(idx, freq_square.shape)
                f_idx = rel_f_idx + f_start
                t_idx = rel_t_idx + t_start
                mag = freq_square[rel_f_idx, rel_t_idx]
                peak_candidates.append((t_idx, f_idx, mag))
                
                # Append the original time index (t_idx), frequency index (f_idx), and magnitude (mag)
                peak_candidates.append((t_idx, f_idx, mag))

        # Keep top peaks per time window (sorted by magnitude)
        proportion_keep = 0.95
        
        # Done TODO: Sort the peak candidates by magnitude, descending
        #pass
        num_peaks_to_keep = max(1,  int(len(peak_candidates) * proportion_keep))
        peak_candidates = peak_candidates[:num_peaks_to_keep]
        for t_idx, f_idx, mag in peak_candidates:
            constellation_map.append((t_idx, f_idx))
        
        # TODO: Keep the top proportion_keep of peak candidates and 
        # append the time index and frequency to the constellation map
        proportion_keep = 0.95
        peak_candidates.sort(key=lambda x: x[2], reverse=True)
        num_peaks_to_keep = max(1, int(len(peak_candidates) * proportion_keep))
        peak_candidates = peak_candidates[:num_peaks_to_keep]

        for t_idx, f_idx, mag in peak_candidates:
            constellation_map.append((t_idx, f_idx))

    # Remove peaks that are too close to each other (treated as duplicates)
    return remove_duplicate_peaks(constellation_map)


def create_constellation_map(audio, sr, hop_length=None) -> list[list[int]]:
    frequencies, times, magnitude = compute_fft(audio, sr, hop_length=hop_length)
    constellation_map = find_peaks(frequencies, times, magnitude)
    return constellation_map
