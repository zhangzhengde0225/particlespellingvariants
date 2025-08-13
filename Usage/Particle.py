import json, pdg
from typing import Dict
from particle import Particle as Particle_external

class Particle:
    _file_cache = None

    def __init__(self, name: str, mother=None, children=None, id: int=0):
        self.name = name
        self.mother = mother
        self.children = children if children is not None else []
        self.id = id

        # 从本地数据库获取基本信息
        item = self.match_particle_name(name)
        if not item:
            raise ValueError(f"Particle {name} not found in database")
    
        self._initialize_from_local_db(item)

        # 尝试从外部API获取更多信息
        try:
            self._initialize_from_external_api()
        except Exception as e:
            print(f"Error in Particle ({self.name}, mcid={self.mcid}) initialization from external API: {e}")

    def _initialize_from_local_db(self, item):
        """从本地数据库初始化基本属性"""
        self.name = item.get("name", "unknown")
        self.mcid = item.get("mcid", 0)
        self.programmatic_name = item.get("programmatic_name", str(self.mcid))
        self.latex_name = item.get("latex_name", str(self.mcid))
        self.evtgen_name = item.get("evtgen_name", str(self.mcid))
        self.html_name = item.get("html_name", str(self.mcid))
        self.unicode_name = item.get("unicode_name", str(self.mcid))

        # 设置默认值
        self.branching_fractions = item.get('branching_fractions', None) # list
        self.charge = item.get('charge', None) # double
        self.exclusive_branching_fractions = item.get('exclusive_branching_fractions', None) # list
        self.has_lifetime_entry = item.get('has_lifetime_entry', None) # bool
        self.has_mass_entry = item.get('has_mass_entry', None) # bool
        self.has_width_entry = item.get('has_width_entry', None) # bool
        self.inclusive_branching_fractions = item.get('inclusive_branching_fractions', None) # list
        self.is_baryon = item.get('is_baryon', None) # bool
        self.is_boson = item.get('is_boson', None) # bool
        self.is_lepton = item.get('is_lepton', None) # bool
        self.is_meson = item.get('is_meson', None) # bool
        self.is_quark = item.get('is_quark', None) # bool
        self.lifetime = item.get('lifetime', None)
        self.lifetime_err = item.get('lifetime_err', None)
        self.mass = item.get('mass', None)
        self.mass_err = item.get('mass_err', None)
        self.quantum_C = item.get('quantum_C', None)
        self.quantum_G = item.get('quantum_G', None)
        self.quantum_I = item.get('quantum_I', None)
        self.quantum_J = item.get('quantum_J', None)
        self.quantum_P = item.get('quantum_P', None)
        self.width = item.get('width', None)
        self.width_err = item.get('width_err', None)

    def _initialize_from_external_api(self):
        """从外部API获取更多属性"""
        api = pdg.connect()
        particle = api.get_particle_by_mcid(self.mcid)

        # 逐个属性判断并获取
        if self.branching_fractions is None:
            self.branching_fractions = particle.branching_fractions()

        if self.charge is None:
            self.charge = particle.charge

        if self.exclusive_branching_fractions is None:
            self.exclusive_branching_fractions = particle.exclusive_branching_fractions()

        if self.has_lifetime_entry is None:
            self.has_lifetime_entry = particle.has_lifetime_entry

        if self.has_mass_entry is None:
            self.has_mass_entry = particle.has_mass_entry

        if self.has_width_entry is None:
            self.has_width_entry = particle.has_width_entry

        if self.inclusive_branching_fractions is None:
            self.inclusive_branching_fractions = particle.inclusive_branching_fractions()

        if self.is_baryon is None:
            self.is_baryon = particle.is_baryon

        if self.is_boson is None:
            self.is_boson = particle.is_boson

        if self.is_lepton is None:
            self.is_lepton = particle.is_lepton

        if self.is_meson is None:
            self.is_meson = particle.is_meson

        if self.is_quark is None:
            self.is_quark = particle.is_quark

        if self.lifetime is None:
            self.lifetime = particle.lifetime

        if self.lifetime_err is None:
            self.lifetime_err = particle.lifetime_error

        if self.mass is None:
            self.mass = particle.mass

        if self.mass_err is None:
            self.mass_err = particle.mass_error

        if self.quantum_C is None:
            self.quantum_C = particle.quantum_C

        if self.quantum_G is None:
            self.quantum_G = particle.quantum_G

        if self.quantum_I is None:
            self.quantum_I = particle.quantum_I

        if self.quantum_J is None:
            self.quantum_J = particle.quantum_J

        if self.quantum_P is None:
            self.quantum_P = particle.quantum_P

        if self.width is None:
            self.width = particle.width

        if self.width_err is None:
            self.width_err = particle.width_error

        # 使用 Particle 包获取额外信息
        particle_ex = Particle_external.findall(lambda p: p.pdgid == self.mcid)
        if particle_ex:
            if self.programmatic_name is None:
                self.programmatic_name = particle_ex[0].programmatic_name
            if self.latex_name is None:
                self.latex_name = particle_ex[0].latex_name
            if self.evtgen_name is None:
                self.evtgen_name = particle_ex[0].evtgen_name
            if self.html_name is None:
                self.html_name = particle_ex[0].html_name
            if self.unicode_name is None:
                self.unicode_name = particle_ex[0].unicode_name
  
    @staticmethod
    def match_particle_name(name: str) -> Dict:
        """模拟从本地数据库匹配粒子名称"""
        if Particle._file_cache is None:
            with open("../particle_variants.json", "r") as f:
                Particle._file_cache = json.load(f)
      
        for item in Particle._file_cache:
            fields = {
                item["name"],
                item["programmatic_name"],
                item["latex_name"],
                item["evtgen_name"],
                item["html_name"],
                item["unicode_name"],
            }
            fields.update(item["aliases"])
            if name is not None and name in fields:
                return item
        return {}

if __name__ == "__main__":
    particle = Particle("pi+")

    print(f"Name: {particle.name}")
    print(f"MCID: {particle.mcid}")
    print(f"Programmatic Name: {particle.programmatic_name}")
    print(f"LaTeX Name: {particle.latex_name}")
    print(f"EvtGen Name: {particle.evtgen_name}")
    print(f"HTML Name: {particle.html_name}")
    print(f"Unicode Name: {particle.unicode_name}")

    # 打印其他属性（如果有）
    print(f"Charge: {particle.charge}")
    print(f"Mass: {particle.mass}")
    print(f"Lifetime: {particle.lifetime}")