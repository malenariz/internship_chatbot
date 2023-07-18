export type Message = Readonly<{
    type: 'user' | 'bot';
    value: string
}>

export type Messages = Array<Message>;