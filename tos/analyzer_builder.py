from tos.analyzers.goroth import GorothAnalyzer
from tos.analyzers.demonic_inq import DIAnalyzer
from tos.analyzers.harjatan import HarjatanAnalyzer
from tos.analyzers.sisters import SistersAnalyzer
from tos.analyzers.host import HostAnalyzer
from tos.analyzers.mistress import MistressAnalyzer
from tos.analyzers.maiden import MaidenAnalyzer
from tos.analyzers.avatar import AvatarAnalyzer
from tos.analyzers.kiljaeden import KiljaedenAnalyzer

tos_fights = {
    2032: GorothAnalyzer,
    2048: DIAnalyzer,
    2036: HarjatanAnalyzer,
    2037: MistressAnalyzer,
    2050: SistersAnalyzer,
    2054: HostAnalyzer,
    2052: MaidenAnalyzer,
    2038: AvatarAnalyzer,
    2051: KiljaedenAnalyzer,
}
