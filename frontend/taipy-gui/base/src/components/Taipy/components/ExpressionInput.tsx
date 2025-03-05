import React, { useEffect } from "react";
import Editor, { useMonaco } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import { Box } from "@mui/material";
import useStore from "../../../store";
import { getVarList } from "../utils";

const THEME_NAME = "expression-theme";
const LANGUAGE_ID = "python-expressions";

const ExpressionInput = (props: TaipyElementInput) => {
    const app = useStore((state) => state.app);
    const monacoInstance = useMonaco();

    useEffect(() => {
        if (
            !app ||
            !monacoInstance ||
            monacoInstance.languages.getLanguages().some((lang) => lang.id === LANGUAGE_ID)
        ) {
            return;
        }

        monacoInstance.editor.defineTheme(THEME_NAME, {
            base: "vs-dark",
            inherit: true,
            rules: [{ token: "expression", foreground: "FFA500", fontStyle: "bold" }],
            colors: {},
        });

        monacoInstance.editor.setTheme(THEME_NAME);

        monacoInstance.languages.register({ id: LANGUAGE_ID });

        monacoInstance.languages.setMonarchTokensProvider(LANGUAGE_ID, {
            tokenizer: {
                root: [[/\{(?:[^{}]|\{[^{}]*\})*\}/, "expression"]],
            },
        });

        monacoInstance.languages.registerCompletionItemProvider(LANGUAGE_ID, {
            triggerCharacters: ["{"],
            provideCompletionItems: (model, position, context) => {
                // const word = model.getWordAtPosition(position);
                // const range = word
                //     ? new monaco.Range(position.lineNumber, word.startColumn, position.lineNumber, word.endColumn)
                //     : new monaco.Range(position.lineNumber, position.column, position.lineNumber, position.column);
                const wordUntil = model.getWordUntilPosition(position);
                const range = new monaco.Range(
                    position.lineNumber,
                    wordUntil.startColumn,
                    position.lineNumber,
                    wordUntil.endColumn,
                );
                const isCurlyTrigger =
                    context.triggerKind === monaco.languages.CompletionTriggerKind.TriggerCharacter &&
                    context.triggerCharacter === "{";

                const suggestions = getVarList(app).map((item) => ({
                    label: item[1],
                    kind: monaco.languages.CompletionItemKind.Variable,
                    insertText: `${isCurlyTrigger ? "" : "{"}${item[0]}}`,
                    range,
                }));

                return {
                    suggestions,
                };
            },
        });
    }, [app, monacoInstance]);

    return (
        <Box
            sx={{
                border: "1px solid #ccc",
                borderRadius: "4px",
                padding: "5px",
                display: "flex",
                width: "100%",
                height: "40px",
                justifyContent: "center",
                alignItems: "center",
            }}
        >
            <Editor
                width="100%"
                height="25px"
                value={(props.value as string) || ""}
                defaultLanguage={LANGUAGE_ID}
                language={LANGUAGE_ID}
                theme={THEME_NAME}
                options={{
                    fontSize: 16,
                    wordWrap: "off",
                    lineNumbers: "off",
                    minimap: { enabled: false },
                    scrollbar: { vertical: "hidden", horizontal: "hidden" },
                    overviewRulerLanes: 0,
                    overviewRulerBorder: false,
                    // automaticLayout: false,
                    folding: false,
                    scrollBeyondLastLine: false,
                    renderLineHighlight: "none",
                    quickSuggestions: true,
                    suggest: { showWords: true, showVariables: true },
                }}
                onMount={(editor, monacoInstance) => {
                    const model = editor.getModel();
                    if (model) {
                        monacoInstance.editor.setModelLanguage(model, LANGUAGE_ID);
                    }
                    editor.onKeyDown((e) => {
                        if (e.keyCode === monaco.KeyCode.Enter) {
                            e.preventDefault();
                        }
                    });
                }}
                onChange={(value) => {
                    if (props.onChange) {
                        props.onChange(value);
                    }
                }}
            />
        </Box>
    );
};

export default ExpressionInput;
