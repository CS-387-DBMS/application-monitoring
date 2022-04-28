import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { RequestsService } from '../requests.service';

@Component({
  selector: 'add-machine',
  templateUrl: './add-machine.component.html',
  styles: [
  ]
})

export class AddMachineComponent implements OnInit {

  Form = new FormGroup(
    {
      MachineName: new FormControl('', Validators.required),
      MachineIP: new FormControl('', Validators.required),
      RAM_usage: new FormControl('', Validators.required),
      CPU_usage: new FormControl('', Validators.required),
      Disk_usage: new FormControl('', Validators.required),
      // n_threads: new FormControl('', Validators.required),
    }
  )

  constructor(private route: ActivatedRoute, private router: Router, private req: RequestsService) { }

  ngOnInit(): void {
  }

  onSubmit(){
    this.req.post(`/input/addmachine/`, this.Form.value).subscribe(
      response => 
      {
        alert("Form Submission Successful")
        //this.Form.reset() 
      },
      error => 
      {
        console.log(error)
        alert("Form Submission Not Successful!\nCheck Again")
      }
    )
  }

}