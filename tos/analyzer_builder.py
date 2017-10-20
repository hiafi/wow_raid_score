from tos.analyzers.goroth import GorothAnalyzer
from tos.analyzers.demonic_inq import DIAnalyzer
from tos.analyzers.harjatan import HarjatanAnalyzer
from tos.analyzers.sisters import SistersAnalyzer
from tos.analyzers.host import HostAnalyzer
from tos.analyzers.mistress import MistressAnalyzer
from tos.analyzers.maiden import MaidenAnalyzer

tos_fights = {
    2032: GorothAnalyzer,
    2048: DIAnalyzer,
    2036: HarjatanAnalyzer,
    2037: MistressAnalyzer,
    2050: SistersAnalyzer,
    2054: HostAnalyzer,
    2052: MaidenAnalyzer,
    # 2038: FA,
    # 2051: KJ,
}
