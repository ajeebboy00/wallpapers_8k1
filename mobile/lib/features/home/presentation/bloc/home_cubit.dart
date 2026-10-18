import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/home_repository.dart';
import 'home_state.dart';

class HomeCubit extends Cubit<HomeState> {
  final HomeRepository _repository;

  HomeCubit(this._repository) : super(const HomeInitial());

  Future<void> loadHomeFeed() async {
    emit(const HomeLoading());
    try {
      final bundle = await _repository.getHomeFeed();
      emit(HomeLoaded(bundle));
    } catch (e) {
      emit(HomeError(e.toString()));
    }
  }

  Future<void> refreshHomeFeed() async {
    try {
      final bundle = await _repository.getHomeFeed();
      emit(HomeLoaded(bundle));
    } catch (e) {
      emit(HomeError(e.toString()));
    }
  }
}
