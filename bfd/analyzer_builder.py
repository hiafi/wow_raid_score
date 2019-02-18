from bfd.analyzers import opulence, conclave, rhastakhan

bfd_fights = {
    2265: None,  # Champions
    2266: None,  # Jadefire
    2263: None,  # Grong
    2271: opulence.OpulenceAnalyzer,
    2268: conclave.ConclaveAnalyzer,
    2272: rhastakhan.RhastakhanAnalyzer,
    2276: None,  # Mekkatorque
    2280: None,  # Blockade
    2281: None,  # Jaina
}
