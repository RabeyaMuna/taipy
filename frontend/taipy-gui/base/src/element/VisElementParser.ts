import viselementsJson from "./viselements.json";

interface UnparsedVisElements {
    blocks?: [string, ElementDetail][];
    controls?: [string, ElementDetail][];
    undocumented?: [string, ElementDetail][];
}

interface ElementDetail {
    properties?: ElementProperty[];
    inherits?: string[];
}

interface ElementProperty {
    name: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    default_property?: any;
    default_value?: unknown;
    type: string;
    doc: string;
    signature?: [string, string][];
    designer_input_types: string[];
}

type VisElementProperties = Record<ElementProperty["name"], ElementProperty>;

type VisElementPropertyOrder = ElementProperty["name"][];

export type VisElementDetails = [VisElementProperties, VisElementPropertyOrder];

type VisElements = Record<string, VisElementDetails>;

class VisElementParser {
    private static instance: VisElementParser;
    private visElements: VisElements;

    private constructor() {
        this.visElements = VisElementParser.parseVisualElements();
    }

    private static parseVisualElements(): VisElements {
        const unparsedVisElements: UnparsedVisElements = viselementsJson as UnparsedVisElements;
        const blocks: Record<string, ElementDetail> = (unparsedVisElements["blocks"] || []).reduce(
            (obj: Record<string, ElementDetail>, v: [string, ElementDetail]) => {
                obj[v[0]] = v[1];
                return obj;
            },
            {} as Record<string, ElementDetail>,
        );
        const controls: Record<string, ElementDetail> = (unparsedVisElements["controls"] || []).reduce(
            (obj: Record<string, ElementDetail>, v: [string, ElementDetail]) => {
                obj[v[0]] = v[1];
                return obj;
            },
            {} as Record<string, ElementDetail>,
        );
        const undocumented: Record<string, ElementDetail> = (unparsedVisElements["undocumented"] || []).reduce(
            (obj: Record<string, ElementDetail>, v: [string, ElementDetail]) => {
                obj[v[0]] = v[1];
                return obj;
            },
            {} as Record<string, ElementDetail>,
        );
        const blocksProperties: Record<string, VisElementDetails> = {};
        const controlsProperties: Record<string, VisElementDetails> = {};
        // handle all blocks object
        Object.keys(blocks).forEach((v: string) => {
            const elementDetail: ElementDetail = blocks[v];
            blocksProperties[v] = VisElementParser.getElementDetailProperties(
                elementDetail,
                blocks,
                controls,
                undocumented,
            );
        });
        Object.keys(controls).forEach((v: string) => {
            const elementDetail: ElementDetail = controls[v];
            controlsProperties[v] = VisElementParser.getElementDetailProperties(
                elementDetail,
                blocks,
                controls,
                undocumented,
            );
        });
        return { ...blocksProperties, ...controlsProperties };
    }

    private static getElementDetailProperties = (
        elementDetail: ElementDetail,
        blocks: Record<string, ElementDetail>,
        controls: Record<string, ElementDetail>,
        undocumented: Record<string, ElementDetail>,
    ): VisElementDetails => {
        const [inheritedProperties, inheritedPropertyOrder] = VisElementParser.handleElementDetailInherits(
            elementDetail.inherits,
            blocks,
            controls,
            undocumented,
        );
        const [propertyList, propertyOrder] = this.parsePropertyList(elementDetail.properties);
        return [
            { ...inheritedProperties, ...propertyList },
            [...new Set([...propertyOrder, ...inheritedPropertyOrder])],
        ];
    };

    private static parsePropertyList(propertyList: ElementProperty[] | undefined): VisElementDetails {
        if (!propertyList) {
            return [{}, []];
        }
        return [
            propertyList.reduce((obj: VisElementProperties, v: ElementProperty) => {
                obj[v.name] = v;
                return obj;
            }, {} as VisElementProperties),
            propertyList.map((v) => v.name),
        ];
    }

    private static handleElementDetailInherits(
        inherits: string[] | undefined,
        blocks: Record<string, ElementDetail>,
        controls: Record<string, ElementDetail>,
        undocumented: Record<string, ElementDetail>,
    ): VisElementDetails {
        if (!inherits) {
            return [{}, []];
        }
        let properties: VisElementProperties = {};
        let propertyOrder: ElementProperty["name"][] = [];
        inherits.forEach((v) => {
            let elementDetail: ElementDetail;
            if (v in undocumented) {
                elementDetail = undocumented[v];
            } else if (v in controls) {
                elementDetail = controls[v];
            } else {
                elementDetail = blocks[v];
            }
            const [elementProperties, elementPropertyOrder] = VisElementParser.getElementDetailProperties(
                elementDetail,
                blocks,
                controls,
                undocumented,
            );
            propertyOrder = [...propertyOrder, ...elementPropertyOrder];
            properties = {
                ...elementProperties,
                ...properties,
            };
        });
        return [properties, propertyOrder];
    }

    public static getInstance(): VisElementParser {
        if (!VisElementParser.instance) {
            VisElementParser.instance = new VisElementParser();
        }
        return VisElementParser.instance;
    }

    public getDesignerProperty(elementType: string): VisElementDetails {
        const [properties, propertyOrder] = this.visElements[elementType];
        if (!properties) {
            console.error(`Element type ${elementType} not found in visual elements`);
            return [{}, []];
        }
        const filteredProperties = propertyOrder.reduce((obj: VisElementProperties, key: string) => {
            const elementProperty = properties[key];
            if ("designer_input_types" in elementProperty) {
                obj[key] = elementProperty;
            }
            return obj;
        }, {} as VisElementProperties);
        return [filteredProperties, propertyOrder.filter((v) => v in filteredProperties)];
    }
}

export default VisElementParser;
