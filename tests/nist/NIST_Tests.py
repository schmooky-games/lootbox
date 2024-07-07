from randomness_testsuite.FrequencyTest import FrequencyTest
from randomness_testsuite.RunTest import RunTest
from randomness_testsuite.Matrix import Matrix
from randomness_testsuite.Spectral import SpectralTest
from randomness_testsuite.TemplateMatching import TemplateMatching
from randomness_testsuite.Universal import Universal
from randomness_testsuite.Complexity import ComplexityTest
from randomness_testsuite.Serial import Serial
from randomness_testsuite.ApproximateEntropy import ApproximateEntropy
from randomness_testsuite.CumulativeSum import CumulativeSums
from randomness_testsuite.RandomExcursions import RandomExcursions


class NIST_Tests:
    def __init__(self):
        pass

    def run(self, binary_data):
        results = {}
        results['frequency_test'] = FrequencyTest.monobit_test(binary_data)[0]
        results['block_frequency_test'] = FrequencyTest.block_frequency(binary_data)[0]
        results['run_test'] = RunTest.run_test(binary_data)[0]
        results['matrix_rank_test'] = Matrix.binary_matrix_rank_text(binary_data)[0]
        results['spectral_test'] = SpectralTest.spectral_test(binary_data)[0]
        results['non_overlapping_template_matching_test'] = TemplateMatching.non_overlapping_test(binary_data)[0]
        results['overlapping_template_matching_test'] = TemplateMatching.overlapping_patterns(binary_data)[0]
        results['universal_test'] = Universal.statistical_test(binary_data)[0]
        results['linear_complexity_test'] = ComplexityTest.linear_complexity_test(binary_data)[0]
        results['serial_test'] = Serial.serial_test(binary_data)[0]
        results['approximate_entropy_test'] = ApproximateEntropy.approximate_entropy_test(binary_data)[0]
        results['cumulative_sums_test'] = CumulativeSums.cumulative_sums_test(binary_data)[0]
        results['random_excursions_test'] = RandomExcursions.random_excursions_test(binary_data)[0]
        results['random_excursions_variant_test'] = RandomExcursions.random_excursions_test(binary_data)[0]
        return results
