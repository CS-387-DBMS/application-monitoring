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

  public MachineArr : any;
  public numbers : number[]  = [];

  Form = new FormGroup(
    {
      MachineName: new FormControl('', Validators.required),
      MachineIP: new FormControl('', Validators.required),
      Port: new FormControl('', Validators.required),
      RAM_usage: new FormControl('', Validators.required),
      CPU_usage: new FormControl('', Validators.required),
      packet: new FormControl('', Validators.required),
      passwrd: new FormControl('', Validators.required),
      // n_threads: new FormControl('', Validators.required),
    }
  )

  constructor(private route: ActivatedRoute, private router: Router, private req: RequestsService) { }

  ngOnInit(): void {
    this.UpdateTable();
  }

  onSubmit() {
    console.log("here");
    console.log(this.Form.value)

    this.req.post(`/input/addmachine/`, this.Form.value).subscribe(
      response => {
        alert("Form Submission Successful")
        this.UpdateTable();
        //this.Form.reset() 
      },
      error => {
        console.log(error)
        alert("Form Submission Not Successful!\nCheck Again")
      }
    )
  }

  UpdateTable(){
    this.req.get(`/input/addmachine/`).subscribe(
      response => {
        console.log(response)
        this.MachineArr = response;
        var v = this.MachineArr.length;
        this.numbers = [];
        for(let i=0; i<v; i++){
          this.numbers.push(i);
        }
      },
      error => {
        console.log(error)
      }
    )
  }

  Delete(num: number){
    console.log("here");
    this.req.del(`/input/delmachine/`, num).subscribe(
      response => {
        alert("Delete Successful")
        this.UpdateTable();
      },
      error => {
        console.log(error)
        alert("Delete Not Successful!\nCheck Again")
      }
    )
  }

  StartMonitoring(){
    this.req.get(`/input/monitor/`).subscribe(
      response => {
        this.router.navigate(['stats'])        
      },
      error => {

      }
    )
  }

}