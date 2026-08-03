

## Project  init/build

1. Install uv, nodejs
2. Sync uv via  `uv sync`
3. Install slidev following instructions from [here](https://sli.dev/guide/).
4. Initiliaze slidev dependency `pnpm up` (not sure?) in the slides directory. 
5. Set PYTHONPATH to the current directory with `'$env:PYTHONPATH=$pwd` in powershell or 
   `export PYTHONPATH=$PYTHONPATH:$(pwd)`
6. Initialize npm

### Building 
1. First, build all slides/generate vue components 
   ```sh
   uv run python .\scripts\build_assets.py --quality l
   ```
2. Build the slides using npm
   ```sh
   npm run dev
   ```

## Command for building individual slides

```sh
uv run manim -pql .\ppidc\slides.py TransposeTransform
```
