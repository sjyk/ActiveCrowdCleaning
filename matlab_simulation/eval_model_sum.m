function error = eval_model_sum(pred_Y, Y)
error = abs(sum(pred_Y) - sum(Y))/sum(Y);