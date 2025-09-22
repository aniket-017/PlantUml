module.exports = {
    apps: [
      {
        name: "PlantUml",
        script: "uvicorn",
        args: "app.main:app --reload --host 154.53.42.27 --port 2004",
        cwd: "/home/admin/PlantUML/plantuml2",
        instances: 1,
        autorestart: true,
        watch: false,
        max_memory_restart: "1G",
        interpreter: "python3",   // 👈 Important fix
        env: {
          NODE_ENV: "production",
        },
        error_file: "./logs/err.log",
        out_file: "./logs/out.log",
        log_file: "./logs/combined.log",
        time: true,
      },
    ],
  };
  