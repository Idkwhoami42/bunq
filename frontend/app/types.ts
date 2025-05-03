export type TripT = {
    id: string;
    name: string;
    creator: string;
    location: {
        name: string;
        lat: number;
        lng: number;
    };
    users: string[];
    started: boolean;
    chat: {
        messages: Message[];
    }
    pot?: Pot;
    locations: Locations[][];
    quiz?: Quiz;
}

export type Message = {
    sender: string;
    content: string;
    timestamp: Date;
    locationIndex?: number;
}

export type Pot = {
    description: string;
    individual_savings: IndividualSaving[];
    shared_savings: SharedSaving[];
}

export type IndividualSaving = {
    description: string;
    participant_amounts: ParticipantAmount[];
}

export type ParticipantAmount = {
    participant: string;
    currency: string;
    expected_amount: number;
    amount_contributed: number;
}

export type SharedSaving = {
    description: string;
    currency: string;
    expected_amount: number;
    amount_contributed: number;
}


export type Locations = {
    name: string;
    google_maps_uri: string;
    website_uri?: string;
    latitude?: number;
    longitude?: number;
};

export type Quiz = {};
