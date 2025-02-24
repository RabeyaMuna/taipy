const path = require("path");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const resolveApp = (relativePath) => path.resolve(__dirname, relativePath);

const moduleName = "TaipyGuiBase";
const basePath = "../../../taipy/gui/webapp";
const taipyGuiBaseExportPath = resolveApp(basePath + "/taipy-gui-base-export");

module.exports = [
    {
        entry: "./base/src/exports.ts",
        output: {
            filename: "taipy-gui-base.js",
            path: taipyGuiBaseExportPath,
            library: {
                name: moduleName,
                type: "umd",
            },
            publicPath: "",
        },
        module: {
            rules: [
                {
                    test: /\.tsx?$/,
                    use: "ts-loader",
                    exclude: /node_modules/,
                },
                {
                    test: /\.css$/,
                    use: ["style-loader", "css-loader"],
                },
            ],
        },
        resolve: {
            extensions: [".tsx", ".ts", ".js", ".tsx"],
        },
        plugins: [
            new CopyWebpackPlugin({
                patterns: [{ from: "./base/src/packaging", to: taipyGuiBaseExportPath }],
            }),
        ],
        externals: {
            react: {
                commonjs: "react",
                commonjs2: "react",
                amd: "react",
                root: "_",
            },
            "react-dom": {
                commonjs: "react-dom",
                commonjs2: "react-dom",
                amd: "react-dom",
                root: "_",
            },
        },
    },
];
