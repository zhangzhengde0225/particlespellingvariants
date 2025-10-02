from typing import Dict, Union, Literal
from dataclasses import dataclass, field
import json, sys
import hepai
from hepai import HRModel, HModelConfig, HWorkerConfig, HWorkerAPP

from pathlib import Path
here = Path(__file__).parent.resolve()

try:
    from ParSV import __version__
except ImportError:
    sys.path.append(str(here.parent.parent))
    from ParSV import __version__
    
from ParSV.Usage.Particle import Particle
from ParSV.worker._response_value_object import ParticleVO

@dataclass  # (1) model config
class CustomModelConfig(HModelConfig):
    name: str = field(default="hepai/particle-spelling-variants", metadata={"help": "Model's name"})
    permission: Union[str, Dict] = field(default=None, metadata={"help": "Model's permission, separated by ;, e.g., 'groups: all; users: a, b; owner: c', will inherit from worker permissions if not setted"})
    version: str = field(default="2.0", metadata={"help": "Model's version"})
    enable_mcp: bool = field(default=True, metadata={"help": "Enable MCP router"})
    mcp_transport: Literal["sse", "streamable-http"] = field(default="sse", metadata={"help": "MCP transport type, could be 'sse' or 'streamable-http'"})


@dataclass  # (2) worker config
class CustomWorkerConfig(HWorkerConfig):
    # config for worker server
    host: str = field(default="0.0.0.0", metadata={"help": "Worker's address, enable to access from outside if set to `0.0.0.0`, otherwise only localhost can access"})
    port: Union[int, str, None] = field(default=42600, metadata={"help": "Worker's port, default is 42600"})
    auto_start_port: int = field(default=42602, metadata={"help": "Worker's start port, only used when port is set to `None`"})
    type: Literal["common", "llm", "actuator", "preceptor", "memory", "tool"] = field(default="common", metadata={"help": "Specify worker type, could be help in some cases"})
    speed: int = field(default=1, metadata={"help": "Model's speed"})
    limit_model_concurrency: int = field(default=100, metadata={"help": "Limit the model's concurrency"})
    permissions: str = field(default='users: admin;groups: payg;owner:zdzhang@ihep.ac.cn', metadata={"help": "Worker's permissions, separated by ;, e.g., 'groups: default; users: a, b; owner: c'"})
    author: str = field(default='zdzhang@ihep.ac.cn', metadata={"help": "Model's author"})
    description: str = field(default='This is a custom remote worker created by HepAI.', metadata={"help": "Model's description"})
    
    # config for controller connection
    controller_address: str = field(default="https://aiapi.ihep.ac.cn", metadata={"help": "Controller's address"})
    # controller_address: str = field(default="http://localhost:42601", metadata={"help": "Controller's address"})
    no_register: bool = field(default=False, metadata={"help": "Do not register to controller"})


class CustomWorkerModel(HRModel):  # Define a custom worker model inheriting from HRModel.
    def __init__(self, config: HModelConfig):
        super().__init__(config=config)

    @HRModel.remote_callable  # Decorate the function to enable remote call.
    def add(self, a: int = 1, b: int = 2) -> int:
        """Define your custom method here."""
        return a + b
    
    @HRModel.remote_callable
    def get_stream(self):
        for x in range(10):
            yield f"data: {json.dumps(x)}\n\n"

    @HRModel.remote_callable
    def particle_name_to_properties(
        self, 
        name: str = None,
        mother: str = None, 
        children: str = None, 
        id: int = 0,
        # **kwargs
        ):
        """ 
        A method to get particle properties by name, the name could be any of the spelling variants.
        For example:
        - name: "pi+"
        - name: "pi_plus"
        - name: "π+"
        """
        assert isinstance(name, str) and len(name) > 0, "name should be a non-empty string."
        particle = Particle(name, mother=mother, children=children, id=id)
        
        resp_vo = ParticleVO(
            # 基本标识信息
            name=particle.name,
            mcid=particle.mcid,
            # 不同格式的名称
            programmatic_name=particle.programmatic_name,
            latex_name=particle.latex_name,
            evtgen_name=particle.evtgen_name,
            html_name=particle.html_name,
            unicode_name=particle.unicode_name,
            # 层次结构
            mother=particle.mother,
            children=particle.children,
            # aliases=particle.aliases,
            # typo=particle.typo,
            # 物理属性
            charge=particle.charge,
            mass=particle.mass,
            mass_err=particle.mass_err,
            lifetime=particle.lifetime,
            lifetime_err=particle.lifetime_err,
            width=particle.width,
            width_err=particle.width_err,
            # 量子数
            quantum_C=particle.quantum_C,
            quantum_G=particle.quantum_G,
            quantum_I=particle.quantum_I,
            quantum_J=particle.quantum_J,
            quantum_P=particle.quantum_P,
            # 粒子类型标识
            is_baryon=particle.is_baryon,
            is_boson=particle.is_boson,
            is_lepton=particle.is_lepton,
            is_meson=particle.is_meson,
            is_quark=particle.is_quark,
            # 衰变分支比
            branching_fractions=
            particle.branching_fractions,
            exclusive_branching_fractions=particle.exclusive_branching_fractions,
            inclusive_branching_fractions=particle.inclusive_branching_fractions,
            # 其他标识
            has_lifetime_entry=particle.has_lifetime_entry,
            has_mass_entry=particle.has_mass_entry,
            has_width_entry=particle.has_width_entry, 
        )
        resp = resp_vo.model_dump()
        return resp
            
if __name__ == "__main__":

    import uvicorn
    from fastapi import FastAPI
    model_config, worker_config = hepai.parse_args((CustomModelConfig, CustomWorkerConfig))
    model = CustomWorkerModel(model_config)  # Instantiate the custom worker model.
    
    app: FastAPI = HWorkerAPP(models=[model], worker_config=worker_config)  # Instantiate the APP, which is a FastAPI application.
    
    print(app.worker.get_worker_info(), flush=True)
    # 启动服务  
    uvicorn.run(app, host=app.host, port=app.port)