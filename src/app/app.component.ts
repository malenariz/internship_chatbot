import { AfterViewChecked, Component, ElementRef, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { first } from 'rxjs/operators';
import { Messages } from './app.model';
import { AppService } from './app.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements AfterViewChecked {
  @ViewChild('messageContainer', { static: false }) messageContainer: ElementRef | undefined;

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  title = 'internbot';

  form = new FormGroup({
    message: new FormControl('')
  });

  get messageControl() {
    return this.form.controls.message as FormControl;
  }

  messages: Messages = [
    {
      type: 'bot',
      value: 'Hello! I am an Aids. I can help you find jobs and internships. How can I assist you today?'
    },
  ];
  loading = false;

  constructor(private svc: AppService) {}

  send() {
    if (this.form.valid && this.messageControl.value) {
      const value = this.messageControl.value;
      this.messages.push({
        type: 'user',
        value
      });
      this.messageControl.reset();
      this.scrollToBottom();
      this.enableLoading();
      this.svc.getResponse(value).pipe(first()).subscribe(
        (val) => {
          console.log(val)
          this.messages.push({
            type: 'bot',
            value: val
          });
          this.scrollToBottom();
          this.disableLoading();
        },
      )
    }
  }

  enableLoading() {
    this.loading = true;
    this.form.disable();
  }

  disableLoading() {
    this.loading = false;
    this.form.enable();
  }

  scrollToBottom() {
    const chatContainer = this.messageContainer?.nativeElement;
    chatContainer.scrollTop = chatContainer?.scrollHeight + 10;
  }
}
