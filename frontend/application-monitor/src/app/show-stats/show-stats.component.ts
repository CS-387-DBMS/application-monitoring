import { Component, OnInit, QueryList } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import Chart from 'chart.js/auto';
import { interval } from 'rxjs';
import { RequestsService } from '../requests.service';


function getRandomColor(j : number, list: any) {
  return list[j];
}

@Component({
  selector: 'app-show-stats',
  templateUrl: './show-stats.component.html',
  styleUrls: ['./show-stats.component.css']
})
export class ShowStatsComponent implements OnInit {

  
  // disp_score_comparison: Boolean = false;
  Linechart!: Chart;
  // team1: number[] = [];
  // team2: number[] = [];

  // disp_comp = "display: None;";
  // disp_pie = "display: None;";
  // intervalId : any;
  runs1: number[] = [];
  // counter: number = 5;

  public alerts_arr: any;

  charts  : Chart[] = [];
  data : any;
  colorlist: String[] = [];
  graphlist: String[] = [];
  columnsToDisplay = ["alert_no","alert_time","MachineName","alert_type","alert_value"];


  constructor(private route: ActivatedRoute, private router: Router, private req: RequestsService){

    this.colorlist = ["red", "green", "blue", "black", "yellow", "orange"]

    interval(1000).subscribe(x => {
      this.updatee();
    });

    interval(1000).subscribe(x => {
      this.getAlerts();
    });

  }

  ngOnInit(): void {

    let AllData = this.req.get(`/data/getdata/`).subscribe(
      response => {
        console.log("successfulll");
        this.data = response;
        console.log(this.data.length);
        console.log("here");
        console.log(response);
        this.display_details();
      }, 
      error => {
        console.log(error);
      }
    )

    let AlertData = this.req.get(`/data/getalertdata/`).subscribe(
      response => {
        this.alerts_arr = response;
      }, 
      error => {
        console.log(error);
      }
    )
    
  } 

  display_details(){

    let len = this.data.length;

    let sixhundred = []
    for(let i=0; i<60; i++){
      sixhundred.push(i+1);
    }

    for(let i=0; i<len; i++){
      
      let s = 'linechart' + i;
      this.graphlist.push(s);
      console.log(this.graphlist)
      
      let Chart_i = new Chart(
        s,
        {
          type: 'line',
          data: {
            labels: sixhundred,
            datasets: []
          },

          options: {
            scales: {
              y: {
                  beginAtZero: true,
                  title: {
                    text: this.data[i].name,
                    display: true
                  }
              },
              x: {
                title: {
                  text: "time",
                  display: true
                }
              },
            }
          }
        }
      )

      let jj = this.data[i].data.length;

      for(let j=0; j<jj; j++){
        console.log("hereeee");
        console.log(this.data[i].data[j].machine_name)
        Chart_i.data.datasets.push(
          {
            label: this.data[i].data[j].machine_name,
            data: this.data[i].data[j].data,
            borderColor: getRandomColor(j, this.colorlist),
            borderWidth: 1,
            tension: 0,
          }
        )
      }
      Chart_i.update()

      this.charts.push(Chart_i);
    }


    // get data for chart

    let runs2: number[] = [];
    let X_data: number[] = [];
    let count: number = 1;
    let radii1: number[] = [];
    let radii2: number[] = [];

    for(let i = 0; i < 10; i++){
      this.runs1.push(Number(i));
      X_data.push(count);

      if(Number(count + i) > 5){
        radii1.push(3);
      }
      else{
        radii1.push(0);
      }

      radii1.push()
      count = count + 1;
    }

    for(let j = 0; j < 10; j++){
      runs2.push(Number(count + j));
  
      if(Number(count + j) > 5){
        radii2.push(3);
      }
      else{
        radii2.push(0);
      }
    }
    //chart

    this.Linechart = new Chart('linechart',{
      type:'line',
      data:{
        labels: X_data,
        datasets:[{
          label: "test-x",
          data:this.runs1,
          borderColor:"red",
          borderWidth:1,
          tension: 0,
          pointRadius:radii1,
        },
        {
          label: "test-y",
          data:runs2,
          borderColor:"green",
          borderWidth:1,
          tension: 0,
          pointRadius: radii2
        }],
      },
      
      options:{
        responsive: false,
        scales: {
          y: {
              beginAtZero: true,
              title: {
                text: "RUNS",
                display: true
              }
          },
          x: {
            title: {
              text: "OVERS",
              display: true
            }
        },
          
      },
      elements: {
        point:{
            radius: 0
        }
    }        
      }          
    })
    //chart ends
  }

  updatee(){

   

    let len = this.data.length;

    let AllData = this.req.get(`/data/getdata/`).subscribe(
      response => {
        
        let res : any = response;
        for(let i=0; i<len; i++){
          
          let jj = this.data[i].data.length
         
          for(let j=0; j<jj; j++){
            
            let kk = this.data[i].data[j].data.length
            for(let k=0; k<kk; k++){
              this.data[i].data[j].data[k] = Number(res[i].data[j].data[k]);
            }
          }

          this.charts[i].update();
        }
      }, 
      error => {console.log(error)}
    )

    
    // let AllData = this.req.get(`/data/getdata/`).subscribe(
    //   response => {
    //     let x : any = response;
    //     let len = x.length;
    //     for(let i=0; i<len; i++){
    //       for(let j=0; j<60; j++){
    //         this.data[i].Machine1[j] = Number(x[i].Machine1[j]);
    //         this.data[i].Machine2[j] = Number(x[i].Machine2[j]);
    //       }
    //       this.charts[i].update();
    //     }
    //   }, 
    //   error => {
    //     console.log(error);
    //   }
    // )
  }

  getAlerts(){
    this.req.get(`/data/getalertdata/`).subscribe(
      response => {
        this.alerts_arr = response;
        console.log(response);
      },
      error => {
        console.log(error)
      }
    )
  }

}