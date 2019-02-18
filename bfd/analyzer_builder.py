from bfd.analyzers import opulence, conclave, rhastakhan, champion, jadefire, grong

bfd_fights = {
    2265: champion.ChampionAnalyzer,  # Champions
    2266: jadefire.JadefireAnalyzer,  # Jadefire
    2263: grong.GrongAnalyzer,  # Grong
    2271: opulence.OpulenceAnalyzer,
    2268: conclave.ConclaveAnalyzer,
    2272: rhastakhan.RhastakhanAnalyzer,
    2276: None,  # Mekkatorque
    2280: None,  # Blockade
    2281: None,  # Jaina
}
