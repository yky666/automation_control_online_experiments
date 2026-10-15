"""Isolated native Engine process; parent terminates the process tree on timeout."""
import json,sys,traceback
from pathlib import Path
def main():
    request_path=Path(sys.argv[1]);out_path=Path(sys.argv[2])
    req=json.loads(request_path.read_text(encoding='utf-8'))
    eng=None
    try:
        import matlab.engine
        eng=matlab.engine.start_matlab('-nodesktop -nosplash')
        eng.addpath(str(Path(__file__).resolve().parents[1]/'matlab'),nargout=0)
        response=eng.labweb_run(json.dumps(req,ensure_ascii=False),nargout=1)
        out_path.write_text(response,encoding='utf-8')
    except Exception:
        traceback.print_exc();sys.exit(1)
    finally:
        if eng is not None:eng.quit()
if __name__=='__main__':main()
