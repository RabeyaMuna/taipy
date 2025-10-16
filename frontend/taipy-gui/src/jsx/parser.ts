/*
 * Copyright 2021-2025 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
import React from "react";

const JSX_INTERPOLATION = /\{\!([a-zA-Z0-9_\.\-]+)\!\}/gs;
const IS_NUMBER = /^-?\d+(\.\d+)?$/;

const parseText = (txt: string, state?: Record<string, unknown>) => {
    if (!JSX_INTERPOLATION.test(txt)) {
        return txt;
    } else {
        return replaceInterpolations(txt, state);
    }
};

const replaceInterpolations = (txt: string, state?: Record<string, unknown>) => {
    JSX_INTERPOLATION.lastIndex = 0; // reset the regex state https://stackoverflow.com/questions/4724701/regexp-exec-returns-null-sporadically
    let interpolations = JSX_INTERPOLATION.exec(txt);
    if (interpolations && interpolations[0] === txt) {
        const interpolationName = interpolations[1];
        if (state && state[interpolationName] !== undefined) {
            return state[interpolationName];
        } else {
            if (interpolationName === "true") {
                return true;
            }
            if (interpolationName === "false") {
                return false;
            }
            if (interpolationName === "null") {
                return null;
            }
            if (IS_NUMBER.test(interpolationName)) {
                const interpolationNumber = Number(interpolationName);
                if (!isNaN(interpolationNumber)) {
                    return interpolationNumber;
                }
            }
            return undefined;
        }
    }
    while (interpolations) {
        const interpolationName = interpolations[1];
        txt = txt.replace(
            `{!${interpolationName}}!}`,
            state && state[interpolationName] !== undefined ? "" + state[interpolationName] : "undefined"
        );
        JSX_INTERPOLATION.lastIndex = 0; // reset the regex state https://stackoverflow.com/questions/4724701/regexp-exec-returns-null-sporadically
        interpolations = JSX_INTERPOLATION.exec(txt);
    }
    return txt;
};

const translate = (
    root: HTMLElement,
    state?: Record<string, unknown>,
    components?: Record<string, React.ComponentType<object>>
): React.ReactNode | null => {
    if (Array.isArray(root) && root.length == 0) return;

    if (root.nodeType === 3) {
        //Textnodes
        if (!root.textContent || root.textContent.trim() === "") return null;
        return "" + parseText(root.textContent, state);
    }
    const children =
        root.childNodes.length > 0
            ? Array.from(root.childNodes)
                  .map((child) => translate(child as HTMLElement, state, components))
                  .filter((c) => c != null)
            : [];

    const comp = components && root.tagName in components ? components[root.tagName] : root.tagName;

    return React.createElement(
        comp,
        Array.from(root.attributes).reduce((acc, attr) => {
            const value = replaceInterpolations(attr.value as string, state);
            if (value !== undefined) {
                acc[attr.name] = value;
            }
            return acc;
        }, {} as Record<string, unknown>),
        children
    );
};

export const parseJSX = (
    jsx: string,
    state?: Record<string, unknown>,
    components?: Record<string, React.ComponentType<object>>
) => {
    const doc = new DOMParser().parseFromString("<span>" + jsx + "</span>", "application/xml");
    if (!doc || doc.children.length !== 1) {
        return [] as React.ReactElement<React.PropsWithChildren<unknown>>[];
    }
    return Array.from(doc.children[0].children).map((child) =>
        translate(child as HTMLElement, state, components)
    ) as React.ReactElement<React.PropsWithChildren<unknown>>[];
};
