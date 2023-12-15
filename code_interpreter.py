import logging
import time
from typing import Optional, Callable, Any, Tuple, List, Union
from e2b.sandbox.process import ProcessMessage

from pydantic import BaseModel, PrivateAttr

from e2b import EnvVars, Sandbox
TIMEOUT=300

logger = logging.getLogger(__name__)


class created_file(BaseModel):
    name: str
    _sandbox: Sandbox = PrivateAttr()

    def __init__(self, sandbox: Sandbox, **data: Any):
        super().__init__(**data)
        self._sandbox = sandbox

    def __hash__(self):
        return hash(self.name)

    def download(self) -> bytes:
        return self._sandbox.download_file(self.name)


class Anycreator(Sandbox):
    template = "anycreator"
    # template = "Python3-DataAnalysis"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cwd: Optional[str] = None,
        env_vars: Optional[EnvVars] = None,
        timeout: Optional[float] = TIMEOUT,
        on_stdout: Optional[Callable[[ProcessMessage], Any]] = None,
        on_stderr: Optional[Callable[[ProcessMessage], Any]] = None,
        on_artifact: Optional[Callable[[created_file], Any]] = None,
        on_exit: Optional[Callable[[int], Any]] = None,
        **kwargs,
    ):
        self.on_artifact = on_artifact
        super().__init__(
            template=self.template,
            api_key=api_key,
            cwd=cwd,
            env_vars=env_vars,
            timeout=timeout,
            on_stdout=on_stdout,
            on_stderr=on_stderr,
            on_exit=on_exit,
            **kwargs,
        )
        self.process.start_and_wait("sudo chmod -R 777 /home",on_stdout=print,on_stderr=print)
        print("Changed permissions")

    def run_python(
        self,
        code: str,
        on_stdout: Optional[Callable[[ProcessMessage], Any]] = None,
        on_stderr: Optional[Callable[[ProcessMessage], Any]] = None,
        on_artifact: Optional[Callable[[created_file], Any]] = None,
        on_exit: Optional[Callable[[int], Any]] = None,
        env_vars: Optional[EnvVars] = None,
        cwd: str = "",
        process_id: Optional[str] = None,
        timeout: Optional[float] = TIMEOUT,
    ) -> Tuple[str, str, List[created_file]]:
        artifacts = set()

        def register_artifacts(event: Any) -> None:
            on_artifact_func = on_artifact or self.on_artifact
            if event.operation == "Create":
                artifact = created_file(name=event.path, sandbox=self)
                artifacts.add(artifact)
                if on_artifact_func:
                    try:
                        on_artifact_func(artifact)
                    except Exception as e:
                        logger.error("Failed to process artifact", exc_info=e)

        watcher = self.filesystem.watch_dir("/home/user/artifacts")
        watcher.add_event_listener(register_artifacts)
        watcher.start()

        epoch_time = time.time()
        codefile_path = f"/tmp/main-{epoch_time}.py"
        self.filesystem.write(codefile_path, code)

        output = self.process.start_and_wait(
            f"{code}",
            on_stdout=on_stdout,
            on_stderr=on_stderr,
            on_exit=on_exit,
            env_vars=env_vars,
            cwd=cwd,
            process_id=process_id,
            timeout=timeout,
        )

        watcher.stop()

        return output.stdout, output.stderr, list(artifacts)

    def _install_packages(
        self,
        command: str,
        package_names: Union[str, List[str]],
        timeout: Optional[float] = TIMEOUT,
    ) -> None:
        if isinstance(package_names, list):
            package_names = " ".join(package_names)

        package_names = package_names.strip()
        if not package_names:
            return

        output = self.process.start_and_wait(
            f"{command} {package_names}", timeout=timeout
        )

        if output.exit_code != 0:
            raise Exception(
                f"Failed to install package {package_names}: {output.stderr}"
            )

    def install_python_packages(
        self, package_names: Union[str, List[str]], timeout: Optional[float] = TIMEOUT
    ) -> None:
        self._install_packages("pip install", package_names, timeout=timeout)

    def install_system_packages(
        self, package_names: Union[str, List[str]], timeout: Optional[float] = TIMEOUT
    ) -> None:
        self._install_packages(
            "sudo apt-get install -y", package_names, timeout=timeout
        )

    def install_npm_packages(
        self, package_names: Union[str, List[str]], timeout: Optional[float] = TIMEOUT
    ) -> None:
        self._install_packages(
            "npm install", package_names, timeout=timeout
        )

CodeInterpreter = Anycreator
